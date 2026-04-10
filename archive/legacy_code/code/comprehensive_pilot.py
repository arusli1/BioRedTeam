import torch
import json
import random
import numpy as np
from transformers import EsmForMaskedLM, EsmTokenizer
import time
from typing import List, Tuple, Dict

def load_pilot_proteins():
    """Load the 5 pilot proteins from data/pilot_proteins.json"""
    with open('data/pilot_proteins.json', 'r') as f:
        return json.load(f)

def get_hydrophobicity_scores():
    """Kyte-Doolittle hydrophobicity scale for identifying surface residues"""
    return {
        'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2
    }

def get_conservation_scores():
    """Simple conservation scores based on BLOSUM62 diagonal (self-substitution scores)"""
    return {
        'A': 4, 'R': 5, 'N': 6, 'D': 6, 'C': 9,
        'Q': 5, 'E': 5, 'G': 6, 'H': 8, 'I': 4,
        'L': 4, 'K': 5, 'M': 5, 'F': 6, 'P': 7,
        'S': 4, 'T': 5, 'W': 11, 'Y': 7, 'V': 4
    }

def random_masking(sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
    """Random masking strategy - baseline approach"""
    seq_list = list(sequence)
    num_to_mask = int(len(seq_list) * mask_rate)
    positions = random.sample(range(len(seq_list)), num_to_mask)

    for pos in positions:
        seq_list[pos] = '<mask>'

    return ''.join(seq_list), sorted(positions)

def conservation_guided_masking(sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
    """Conservation-guided masking - prefer to mask less conserved residues"""
    conservation = get_conservation_scores()
    seq_list = list(sequence)
    num_to_mask = int(len(seq_list) * mask_rate)

    # Calculate conservation scores for each position
    position_scores = []
    for i, aa in enumerate(sequence):
        score = conservation.get(aa, 5)  # Default score of 5 for unknown AA
        position_scores.append((i, score))

    # Sort by conservation score (ascending - less conserved first)
    position_scores.sort(key=lambda x: x[1])

    # Mask the least conserved positions
    positions = [pos for pos, _ in position_scores[:num_to_mask]]

    for pos in positions:
        seq_list[pos] = '<mask>'

    return ''.join(seq_list), sorted(positions)

def surface_exposed_masking(sequence: str, mask_rate: float) -> Tuple[str, List[int]]:
    """Surface-exposed masking - prefer to mask hydrophilic (surface) residues"""
    hydrophobicity = get_hydrophobicity_scores()
    seq_list = list(sequence)
    num_to_mask = int(len(seq_list) * mask_rate)

    # Calculate hydrophobicity scores for each position
    position_scores = []
    for i, aa in enumerate(sequence):
        score = hydrophobicity.get(aa, 0)  # Default score of 0 for unknown AA
        position_scores.append((i, score))

    # Sort by hydrophobicity (ascending - most hydrophilic/surface-exposed first)
    position_scores.sort(key=lambda x: x[1])

    # Mask the most hydrophilic positions
    positions = [pos for pos, _ in position_scores[:num_to_mask]]

    for pos in positions:
        seq_list[pos] = '<mask>'

    return ''.join(seq_list), sorted(positions)

def generate_variants(model, tokenizer, masked_sequence: str, device, num_variants: int = 5) -> List[str]:
    """Generate variants from masked sequence using ESM-2"""
    inputs = tokenizer(masked_sequence, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    variants = []
    with torch.no_grad():
        outputs = model(**inputs)

        # Find mask positions
        mask_token_id = tokenizer.mask_token_id
        mask_positions = (inputs['input_ids'] == mask_token_id).nonzero(as_tuple=True)[1]

        for _ in range(num_variants):
            variant_ids = inputs['input_ids'].clone()

            for pos in mask_positions:
                # Get top-k predictions for this position
                logits = outputs.logits[0, pos]
                top_tokens = torch.topk(logits, k=5).indices

                # Randomly sample from top-5
                chosen_token = random.choice(top_tokens.tolist())
                variant_ids[0, pos] = chosen_token

            # Decode back to sequence
            variant_seq = tokenizer.decode(variant_ids[0], skip_special_tokens=True)
            # Remove spaces (ESM tokenizer adds them)
            variant_seq = variant_seq.replace(' ', '')
            variants.append(variant_seq)

    return variants

def calculate_sequence_identity(seq1: str, seq2: str) -> float:
    """Calculate sequence identity between two sequences"""
    if len(seq1) != len(seq2):
        return 0.0
    return sum(1 for a, b in zip(seq1, seq2) if a == b) / len(seq1)

def main():
    print("=== ProtBreaker Comprehensive Pilot ===")
    print("Testing ESM-2 650M across systematic parameter space")
    print("5 proteins × 4 masking rates × 3 strategies × 5 variants = 300 total variants\n")

    # Load proteins
    proteins = load_pilot_proteins()
    print(f"Loaded {len(proteins)} pilot proteins:")
    for pid, pdata in proteins.items():
        print(f"  - {pid}: {pdata['name']} ({pdata['length']} AA, {pdata['family']}, Tier {pdata['tier']})")

    # Load ESM-2 model
    print("\nLoading ESM-2 650M...")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tokenizer = EsmTokenizer.from_pretrained("facebook/esm2_t33_650M_UR50D")
    model = EsmForMaskedLM.from_pretrained("facebook/esm2_t33_650M_UR50D")
    model = model.to(device)
    model.eval()
    print(f"Model loaded on {device}")
    print(f"VRAM usage: {torch.cuda.memory_allocated()/1e9:.2f} GB")

    # Experimental parameters
    masking_rates = [0.1, 0.3, 0.5, 0.7]
    masking_strategies = {
        'random': random_masking,
        'conservation': conservation_guided_masking,
        'surface': surface_exposed_masking
    }
    variants_per_config = 5

    print(f"\nMasking rates: {masking_rates}")
    print(f"Masking strategies: {list(masking_strategies.keys())}")
    print(f"Variants per configuration: {variants_per_config}")

    # Results storage
    comprehensive_results = {
        'metadata': {
            'model': 'ESM-2 650M',
            'proteins': len(proteins),
            'masking_rates': masking_rates,
            'masking_strategies': list(masking_strategies.keys()),
            'variants_per_config': variants_per_config,
            'total_variants': len(proteins) * len(masking_rates) * len(masking_strategies) * variants_per_config,
            'timestamp': int(time.time())
        },
        'proteins': {}
    }

    total_configs = len(proteins) * len(masking_rates) * len(masking_strategies)
    current_config = 0

    # Main experimental loop
    for protein_id, protein_data in proteins.items():
        print(f"\n=== Processing {protein_id} ({protein_data['name']}) ===")
        sequence = protein_data['sequence']

        comprehensive_results['proteins'][protein_id] = {
            'name': protein_data['name'],
            'family': protein_data['family'],
            'tier': protein_data['tier'],
            'length': len(sequence),
            'original_sequence': sequence,
            'configurations': {}
        }

        for mask_rate in masking_rates:
            for strategy_name, strategy_func in masking_strategies.items():
                current_config += 1
                config_id = f"{strategy_name}_{int(mask_rate*100)}pct"

                print(f"  Config {current_config}/{total_configs}: {strategy_name} masking at {mask_rate*100:.0f}%")

                # Apply masking strategy
                masked_seq, masked_positions = strategy_func(sequence, mask_rate)
                num_masked = len(masked_positions)

                print(f"    Masked {num_masked} positions ({num_masked/len(sequence)*100:.1f}%)")

                # Generate variants
                variants = generate_variants(model, tokenizer, masked_seq, device, variants_per_config)

                # Calculate sequence identities
                variant_data = []
                identities = []

                for i, variant in enumerate(variants):
                    identity = calculate_sequence_identity(sequence, variant)
                    identities.append(identity)

                    variant_data.append({
                        'variant_id': i + 1,
                        'sequence': variant,
                        'sequence_identity': identity,
                        'length': len(variant)
                    })

                # Store configuration results
                comprehensive_results['proteins'][protein_id]['configurations'][config_id] = {
                    'masking_strategy': strategy_name,
                    'masking_rate': mask_rate,
                    'masked_sequence': masked_seq,
                    'masked_positions': masked_positions,
                    'num_masked_positions': num_masked,
                    'variants': variant_data,
                    'statistics': {
                        'mean_identity': np.mean(identities),
                        'std_identity': np.std(identities),
                        'min_identity': np.min(identities),
                        'max_identity': np.max(identities)
                    }
                }

                print(f"    Generated {len(variants)} variants")
                print(f"    Identity: {np.mean(identities)*100:.1f}±{np.std(identities)*100:.1f}% "
                      f"(range: {np.min(identities)*100:.1f}-{np.max(identities)*100:.1f}%)")

    # Save comprehensive results
    timestamp = comprehensive_results['metadata']['timestamp']
    output_file = f'results/comprehensive_pilot_{timestamp}.json'

    with open(output_file, 'w') as f:
        json.dump(comprehensive_results, f, indent=2)

    print(f"\n=== Comprehensive Pilot Complete ===")
    print(f"Generated {comprehensive_results['metadata']['total_variants']} variants")
    print(f"Results saved to: {output_file}")

    # Summary statistics
    print(f"\n=== Summary Statistics ===")
    all_identities = []
    strategy_stats = {strategy: [] for strategy in masking_strategies.keys()}
    rate_stats = {rate: [] for rate in masking_rates}

    for protein_id, protein_data in comprehensive_results['proteins'].items():
        for config_id, config_data in protein_data['configurations'].items():
            mean_identity = config_data['statistics']['mean_identity']
            all_identities.append(mean_identity)

            strategy = config_data['masking_strategy']
            rate = config_data['masking_rate']

            strategy_stats[strategy].append(mean_identity)
            rate_stats[rate].append(mean_identity)

    print(f"Overall mean sequence identity: {np.mean(all_identities)*100:.1f}±{np.std(all_identities)*100:.1f}%")

    print(f"\nBy masking strategy:")
    for strategy, identities in strategy_stats.items():
        print(f"  {strategy}: {np.mean(identities)*100:.1f}±{np.std(identities)*100:.1f}%")

    print(f"\nBy masking rate:")
    for rate, identities in rate_stats.items():
        print(f"  {rate*100:.0f}%: {np.mean(identities)*100:.1f}±{np.std(identities)*100:.1f}%")

    print(f"\nNext step: Run 'python code/screen_all_variants.py' to screen all {comprehensive_results['metadata']['total_variants']} variants")

if __name__ == "__main__":
    # Set seeds for reproducibility
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)

    main()