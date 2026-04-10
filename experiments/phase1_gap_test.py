"""
Phase 1: Ikonomova Gap Stress-Test

Main experiment to test if protein foundation models cross the structure + function + evasion threshold.
"""

import sys
import os
import json
import time
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import torch
import random
import numpy as np

from models.loader import load_model_and_tokenizer, ModelRegistry
from attacks.masking import get_masking_strategy
from screening.multi_tool import MultiToolScreener, create_blast_database
from analysis.metrics import (
    calculate_sequence_identity, calculate_asps, estimate_tm_score,
    assess_ikonomova_gap, calculate_threshold_metrics
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_protein_data(data_path: str = 'data/pilot_proteins.json') -> dict:
    """Load protein dataset"""
    with open(data_path, 'r') as f:
        return json.load(f)

def generate_variants(model, tokenizer, masked_sequence: str, device: torch.device,
                     num_variants: int = 5) -> list:
    """Generate variants using protein foundation model"""
    inputs = tokenizer(masked_sequence, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    variants = []
    with torch.no_grad():
        outputs = model(**inputs)

        # Handle different model architectures
        if hasattr(outputs, 'logits'):
            logits = outputs.logits
        else:
            logits = outputs.last_hidden_state

        mask_token_id = tokenizer.mask_token_id
        mask_positions = (inputs['input_ids'] == mask_token_id).nonzero(as_tuple=True)[1]

        for _ in range(num_variants):
            variant_ids = inputs['input_ids'].clone()
            for pos in mask_positions:
                if pos < logits.size(1):
                    position_logits = logits[0, pos]
                    top_tokens = torch.topk(position_logits, k=5).indices
                    chosen_token = random.choice(top_tokens.tolist())
                    variant_ids[0, pos] = chosen_token

            variant_seq = tokenizer.decode(variant_ids[0], skip_special_tokens=True)
            variant_seq = variant_seq.replace(' ', '')
            variants.append(variant_seq)

    return variants

def run_gap_test(model_key: str, proteins: dict, screener: MultiToolScreener,
                masking_rates: list, variants_per_config: int = 5) -> dict:
    """Run the main gap test experiment"""

    logger.info(f"Starting gap test for model: {model_key}")

    # Set up model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, tokenizer = load_model_and_tokenizer(model_key, device)

    logger.info(f"Model loaded on {device}")
    logger.info(f"VRAM usage: {torch.cuda.memory_allocated()/1e9:.2f} GB")

    # Initialize results
    results = {
        'metadata': {
            'model': model_key,
            'masking_rates': masking_rates,
            'variants_per_config': variants_per_config,
            'timestamp': int(time.time())
        },
        'proteins': {},
        'gap_analysis': {
            'total_variants': 0,
            'crossed_gap': 0
        }
    }

    total_variants = 0
    crossed_gap = 0
    masking_strategy = get_masking_strategy('random')

    # Process each protein
    for protein_id, protein_data in proteins.items():
        logger.info(f"Processing {protein_id} ({protein_data['name']})")
        sequence = protein_data['sequence']

        results['proteins'][protein_id] = {
            'name': protein_data['name'],
            'length': len(sequence),
            'original_sequence': sequence,
            'masking_results': {}
        }

        # Test each masking rate
        for mask_rate in masking_rates:
            logger.info(f"  Masking rate: {mask_rate*100:.0f}%")

            # Generate masked sequence
            masked_seq, masked_positions = masking_strategy.mask_sequence(sequence, mask_rate)

            # Generate variants
            variants = generate_variants(model, tokenizer, masked_seq, device, variants_per_config)

            variant_results = []
            config_crossed = 0

            for i, variant in enumerate(variants):
                variant_id = f"{protein_id}_{model_key}_{int(mask_rate*100)}pct_v{i+1}"

                # Calculate metrics
                identity = calculate_sequence_identity(sequence, variant)
                tm_score = estimate_tm_score(sequence, variant)
                asps = calculate_asps(sequence, variant, protein_id)

                # Screen variant
                screening_results = screener.screen_comprehensive(variant, variant_id)
                joint_evasion = screener.assess_joint_evasion(screening_results)

                # Assess gap crossing
                gap_assessment = assess_ikonomova_gap(joint_evasion, tm_score, asps)

                variant_result = {
                    'variant_id': i + 1,
                    'sequence_identity': identity,
                    'tm_score': tm_score,
                    'asps': asps,
                    'screening': {k: v.to_dict() for k, v in screening_results.items()},
                    'joint_evasion': joint_evasion,
                    'gap_assessment': gap_assessment
                }

                # Track gap crossing
                if gap_assessment['crosses_gap']:
                    config_crossed += 1
                    crossed_gap += 1
                    logger.info(f"    Variant {i+1}: 🚨 CROSSES GAP! (Identity: {identity*100:.1f}%, TM: {tm_score:.2f}, ASPS: {asps:.2f})")
                else:
                    status = []
                    if gap_assessment['evasive']: status.append("Evasive")
                    if gap_assessment['structural']: status.append("Structural")
                    if gap_assessment['functional']: status.append("Functional")
                    logger.info(f"    Variant {i+1}: {' + '.join(status) if status else 'None'} (Identity: {identity*100:.1f}%, TM: {tm_score:.2f}, ASPS: {asps:.2f})")

                variant_results.append(variant_result)
                total_variants += 1

            # Store configuration results
            results['proteins'][protein_id]['masking_results'][f'{int(mask_rate*100)}pct'] = {
                'mask_rate': mask_rate,
                'variants': variant_results,
                'crossed_gap': config_crossed,
                'gap_rate': config_crossed / len(variants)
            }

            logger.info(f"    Gap crossing rate: {config_crossed}/{len(variants)} ({config_crossed/len(variants)*100:.1f}%)")

    # Update summary statistics
    results['gap_analysis']['total_variants'] = total_variants
    results['gap_analysis']['crossed_gap'] = crossed_gap
    results['gap_analysis']['gap_crossing_rate'] = crossed_gap / total_variants if total_variants > 0 else 0

    return results

def main():
    parser = argparse.ArgumentParser(description='Phase 1: Ikonomova Gap Stress-Test')
    parser.add_argument('--model', choices=ModelRegistry.list_models(), default='esm2_650m',
                       help='Model to test')
    parser.add_argument('--masking_rates', nargs='+', type=float, default=[0.85, 0.90],
                       help='Masking rates to test')
    parser.add_argument('--variants_per_config', type=int, default=5,
                       help='Variants to generate per configuration')
    parser.add_argument('--data_path', default='data/pilot_proteins.json',
                       help='Path to protein data file')
    parser.add_argument('--database_path', default='data/pilot_threat_db',
                       help='Path to screening database')
    parser.add_argument('--output_dir', default='results',
                       help='Output directory for results')

    args = parser.parse_args()

    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    logger.info("=== PHASE 1: IKONOMOVA GAP STRESS-TEST ===")
    logger.info(f"Model: {args.model}")
    logger.info(f"Masking rates: {args.masking_rates}")
    logger.info("Testing if models cross structure + function + evasion threshold")

    # Load data
    proteins = load_protein_data(args.data_path)
    logger.info(f"Loaded {len(proteins)} proteins")

    # Set up screening
    screener = MultiToolScreener(args.database_path)

    # Run experiment
    results = run_gap_test(
        args.model, proteins, screener,
        args.masking_rates, args.variants_per_config
    )

    # Save results
    timestamp = results['metadata']['timestamp']
    output_file = Path(args.output_dir) / f"gap_test_{args.model}_{timestamp}.json"
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Calculate and display threshold metrics
    threshold_metrics = calculate_threshold_metrics(results)

    logger.info("\n=== RESULTS ===")
    logger.info(f"Model tested: {args.model}")
    logger.info(f"Total variants: {threshold_metrics['total_variants']}")
    logger.info(f"Crossed gap: {threshold_metrics['crossed_gap']}")
    logger.info(f"Gap crossing rate: {threshold_metrics['gap_crossing_rate']*100:.1f}%")
    logger.info(f"Risk level: {threshold_metrics['risk_level']}")
    logger.info(f"Status: {threshold_metrics['status']}")
    logger.info(f"Results saved to: {output_file}")

    # Recommendation
    if threshold_metrics['status'] == 'CROSSED':
        logger.info("🚨 THRESHOLD CROSSED: Proceed to Phase 2 (Defense mechanisms)")
    elif threshold_metrics['status'] == 'MONITORING':
        logger.info("⚠️  ENHANCED MONITORING: Prepare for Phase 2")
    else:
        logger.info("✅ SAFE: Continue monitoring and publication preparation")

if __name__ == "__main__":
    main()