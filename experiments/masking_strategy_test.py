#!/usr/bin/env python3
"""
Masking Strategy Validation Test

Tests different masking strategies (random, conservation-guided, surface-exposed)
to validate biological hypotheses about structure-function-evasion tradeoffs.
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

def run_masking_strategy_test():
    """Test different masking strategies to validate biological hypotheses"""

    logger.info("=== MASKING STRATEGY VALIDATION TEST ===")
    logger.info("Testing H4: Masking regime hypothesis")
    logger.info("Comparing random vs conservation-guided vs surface-exposed masking")

    # Set random seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    # Setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model, tokenizer = load_model_and_tokenizer('esm2_650m', device)
    screener = MultiToolScreener('data/pilot_threat_db')
    proteins = load_protein_data('data/pilot_proteins.json')

    # Test parameters
    strategies = ['random', 'conservation', 'surface']
    masking_rates = [0.80, 0.85, 0.90]
    variants_per_config = 5

    results = {
        'metadata': {
            'experiment': 'masking_strategy_test',
            'model': 'esm2_650m',
            'strategies': strategies,
            'masking_rates': masking_rates,
            'variants_per_config': variants_per_config,
            'timestamp': int(time.time())
        },
        'strategies': {}
    }

    # Test each strategy
    for strategy_name in strategies:
        logger.info(f"\n--- Testing {strategy_name} masking ---")
        strategy = get_masking_strategy(strategy_name)

        results['strategies'][strategy_name] = {}

        # Test each masking rate
        for mask_rate in masking_rates:
            logger.info(f"  Masking rate: {mask_rate*100:.0f}%")

            rate_results = {
                'mask_rate': mask_rate,
                'proteins': {},
                'summary': {
                    'total_variants': 0,
                    'evasive_variants': 0,
                    'functional_variants': 0,
                    'structural_variants': 0,
                    'gap_crossing': 0
                }
            }

            # Test key proteins (ricin_a and botox_a for speed)
            test_proteins = ['ricin_a', 'botox_a']

            for protein_id in test_proteins:
                protein_data = proteins[protein_id]
                sequence = protein_data['sequence']

                logger.info(f"    Testing {protein_id}")

                # Generate masked sequence
                masked_seq, masked_positions = strategy.mask_sequence(sequence, mask_rate)

                # Generate variants
                variants = generate_variants(model, tokenizer, masked_seq, device, variants_per_config)

                protein_results = []

                for i, variant in enumerate(variants):
                    # Calculate metrics
                    identity = calculate_sequence_identity(sequence, variant)
                    tm_score = estimate_tm_score(sequence, variant)
                    asps = calculate_asps(sequence, variant, protein_id)

                    # Screen variant
                    screening_results = screener.screen_comprehensive(variant, f"{protein_id}_{strategy_name}_{int(mask_rate*100)}_{i}")
                    joint_evasion = screener.assess_joint_evasion(screening_results)

                    # Assess gap crossing
                    gap_assessment = assess_ikonomova_gap(joint_evasion, tm_score, asps)

                    # Update summary stats
                    rate_results['summary']['total_variants'] += 1
                    if gap_assessment['evasive']:
                        rate_results['summary']['evasive_variants'] += 1
                    if gap_assessment['functional']:
                        rate_results['summary']['functional_variants'] += 1
                    if gap_assessment['structural']:
                        rate_results['summary']['structural_variants'] += 1
                    if gap_assessment['crosses_gap']:
                        rate_results['summary']['gap_crossing'] += 1

                    protein_results.append({
                        'variant_id': i + 1,
                        'sequence_identity': identity,
                        'tm_score': tm_score,
                        'asps': asps,
                        'joint_evasion': joint_evasion,
                        'gap_assessment': gap_assessment
                    })

                rate_results['proteins'][protein_id] = protein_results

            # Calculate rates
            total = rate_results['summary']['total_variants']
            rate_results['summary']['evasion_rate'] = rate_results['summary']['evasive_variants'] / total
            rate_results['summary']['function_rate'] = rate_results['summary']['functional_variants'] / total
            rate_results['summary']['structure_rate'] = rate_results['summary']['structural_variants'] / total
            rate_results['summary']['gap_crossing_rate'] = rate_results['summary']['gap_crossing'] / total

            logger.info(f"    Results: Evasion {rate_results['summary']['evasion_rate']*100:.1f}%, Function {rate_results['summary']['function_rate']*100:.1f}%, Gap crossing {rate_results['summary']['gap_crossing_rate']*100:.1f}%")

            results['strategies'][strategy_name][f'{int(mask_rate*100)}pct'] = rate_results

    # Save results
    timestamp = results['metadata']['timestamp']
    output_file = Path('results') / f'masking_strategy_test_{timestamp}.json'
    output_file.parent.mkdir(exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Report findings
    logger.info("\n=== MASKING STRATEGY TEST RESULTS ===")
    for strategy_name in strategies:
        logger.info(f"\n{strategy_name.upper()} MASKING:")
        for rate_key, rate_data in results['strategies'][strategy_name].items():
            rate = rate_data['mask_rate']
            summary = rate_data['summary']
            logger.info(f"  {rate*100:.0f}%: Evasion {summary['evasion_rate']*100:.1f}%, Function {summary['function_rate']*100:.1f}%, Gap {summary['gap_crossing_rate']*100:.1f}%")

    logger.info(f"\nResults saved to: {output_file}")
    logger.info("Analysis: Testing biological realism of different masking approaches")

    return results

if __name__ == "__main__":
    run_masking_strategy_test()