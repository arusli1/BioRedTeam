#!/usr/bin/env python3
"""
Extended Protein Test

Test more proteins from our dataset to strengthen statistical power
and validate family-specific patterns (H3 from revised plan).
"""

import sys
import os
import json
import time
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import torch
import random
import numpy as np

from models.loader import load_model_and_tokenizer
from attacks.masking import get_masking_strategy
from screening.multi_tool import MultiToolScreener
from analysis.metrics import (
    calculate_sequence_identity, calculate_asps, estimate_tm_score,
    assess_ikonomova_gap
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_full_protein_data() -> dict:
    """Load full protein dataset and extract the actual proteins dict"""
    with open('data/proteins.json', 'r') as f:
        data = json.load(f)

    # Extract just the proteins dictionary
    return data['proteins']

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

def run_extended_protein_test():
    """Test extended protein set to validate family-specific patterns"""

    logger.info("=== EXTENDED PROTEIN TEST ===")
    logger.info("Testing H3: Family specificity hypothesis")
    logger.info("Validating patterns across protein families")

    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, tokenizer = load_model_and_tokenizer('esm2_650m', device)
    screener = MultiToolScreener('data/pilot_threat_db')
    proteins = load_full_protein_data()

    # Test parameters - focus on critical evasion threshold
    masking_rates = [0.85, 0.90]
    variants_per_protein = 8  # More variants per protein for better stats

    results = {
        'metadata': {
            'experiment': 'extended_protein_test',
            'model': 'esm2_650m',
            'masking_rates': masking_rates,
            'variants_per_protein': variants_per_protein,
            'timestamp': int(time.time())
        },
        'proteins': {},
        'family_analysis': {}
    }

    # Process all proteins
    masking_strategy = get_masking_strategy('random')

    for protein_id, protein_data in proteins.items():
        logger.info(f"\n--- Testing {protein_id} ({protein_data['name']}) ---")
        logger.info(f"Family: {protein_data['family']}, Tier: {protein_data['tier']}")

        sequence = protein_data['sequence']

        protein_results = {
            'name': protein_data['name'],
            'family': protein_data['family'],
            'tier': protein_data['tier'],
            'length': len(sequence),
            'masking_results': {}
        }

        # Test each masking rate
        for mask_rate in masking_rates:
            logger.info(f"  Masking rate: {mask_rate*100:.0f}%")

            # Generate masked sequence
            masked_seq, masked_positions = masking_strategy.mask_sequence(sequence, mask_rate)

            # Generate variants
            variants = generate_variants(model, tokenizer, masked_seq, device, variants_per_protein)

            variant_results = []
            evasive_count = 0
            functional_count = 0
            structural_count = 0
            gap_crossing_count = 0

            for i, variant in enumerate(variants):
                # Calculate metrics
                identity = calculate_sequence_identity(sequence, variant)
                tm_score = estimate_tm_score(sequence, variant)
                asps = calculate_asps(sequence, variant, protein_id)

                # Screen variant
                screening_results = screener.screen_comprehensive(variant, f"{protein_id}_{int(mask_rate*100)}_{i}")
                joint_evasion = screener.assess_joint_evasion(screening_results)

                # Assess gap crossing
                gap_assessment = assess_ikonomova_gap(joint_evasion, tm_score, asps)

                # Count capabilities
                if gap_assessment['evasive']:
                    evasive_count += 1
                if gap_assessment['functional']:
                    functional_count += 1
                if gap_assessment['structural']:
                    structural_count += 1
                if gap_assessment['crosses_gap']:
                    gap_crossing_count += 1

                variant_results.append({
                    'variant_id': i + 1,
                    'sequence_identity': identity,
                    'tm_score': tm_score,
                    'asps': asps,
                    'joint_evasion': joint_evasion,
                    'gap_assessment': gap_assessment
                })

            # Calculate rates
            total_variants = len(variants)
            evasion_rate = evasive_count / total_variants
            function_rate = functional_count / total_variants
            structure_rate = structural_count / total_variants
            gap_rate = gap_crossing_count / total_variants

            protein_results['masking_results'][f'{int(mask_rate*100)}pct'] = {
                'mask_rate': mask_rate,
                'variants': variant_results,
                'statistics': {
                    'total_variants': total_variants,
                    'evasive_variants': evasive_count,
                    'functional_variants': functional_count,
                    'structural_variants': structural_count,
                    'gap_crossing': gap_crossing_count,
                    'evasion_rate': evasion_rate,
                    'function_rate': function_rate,
                    'structure_rate': structure_rate,
                    'gap_rate': gap_rate
                }
            }

            logger.info(f"    Results: Evasion {evasion_rate*100:.1f}%, Function {function_rate*100:.1f}%, Structure {structure_rate*100:.1f}%, Gap {gap_rate*100:.1f}%")

        results['proteins'][protein_id] = protein_results

    # Analyze by family
    families = {}
    for protein_id, protein_data in results['proteins'].items():
        family = protein_data['family']
        if family not in families:
            families[family] = []
        families[family].append(protein_id)

    for family, protein_ids in families.items():
        logger.info(f"\n--- {family.upper()} FAMILY ANALYSIS ---")

        family_stats = {
            'proteins': protein_ids,
            'count': len(protein_ids),
            'masking_rates': {}
        }

        for mask_rate in masking_rates:
            rate_key = f'{int(mask_rate*100)}pct'

            # Aggregate stats across proteins in family
            total_variants = 0
            total_evasive = 0
            total_functional = 0
            total_structural = 0
            total_gap_crossing = 0

            for protein_id in protein_ids:
                stats = results['proteins'][protein_id]['masking_results'][rate_key]['statistics']
                total_variants += stats['total_variants']
                total_evasive += stats['evasive_variants']
                total_functional += stats['functional_variants']
                total_structural += stats['structural_variants']
                total_gap_crossing += stats['gap_crossing']

            family_stats['masking_rates'][rate_key] = {
                'total_variants': total_variants,
                'evasion_rate': total_evasive / total_variants if total_variants > 0 else 0,
                'function_rate': total_functional / total_variants if total_variants > 0 else 0,
                'structure_rate': total_structural / total_variants if total_variants > 0 else 0,
                'gap_rate': total_gap_crossing / total_variants if total_variants > 0 else 0
            }

            stats_summary = family_stats['masking_rates'][rate_key]
            logger.info(f"  {mask_rate*100:.0f}%: Evasion {stats_summary['evasion_rate']*100:.1f}%, Function {stats_summary['function_rate']*100:.1f}%, Gap {stats_summary['gap_rate']*100:.1f}%")

        results['family_analysis'][family] = family_stats

    # Save results
    timestamp = results['metadata']['timestamp']
    output_file = Path('results') / f'extended_protein_test_{timestamp}.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Summary report
    logger.info(f"\n=== EXTENDED PROTEIN TEST SUMMARY ===")
    total_proteins = len(results['proteins'])
    total_variants = sum(
        sum(config['statistics']['total_variants']
            for config in protein_data['masking_results'].values())
        for protein_data in results['proteins'].values()
    )
    logger.info(f"Tested {total_proteins} proteins, {total_variants} total variants")

    logger.info("\nFamily-specific findings:")
    for family, family_data in results['family_analysis'].items():
        logger.info(f"{family}: {family_data['count']} proteins")
        for rate_key, stats in family_data['masking_rates'].items():
            logger.info(f"  {rate_key}: {stats['evasion_rate']*100:.1f}% evasion, {stats['gap_rate']*100:.1f}% gap crossing")

    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Analysis: Statistical validation across protein families")

    return results

if __name__ == "__main__":
    run_extended_protein_test()