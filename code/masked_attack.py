import torch
import json
import random
from transformers import EsmForMaskedLM, EsmTokenizer
import time

def load_test_proteins():
    with open('data/test_proteins.json', 'r') as f:
        return json.load(f)

def mask_sequence(sequence, mask_rate=0.3):
    """Randomly mask amino acids in sequence"""
    seq_list = list(sequence)
    num_to_mask = int(len(seq_list) * mask_rate)
    positions = random.sample(range(len(seq_list)), num_to_mask)

    for pos in positions:
        seq_list[pos] = '<mask>'

    return ''.join(seq_list), positions

def generate_variants(model, tokenizer, masked_sequence, device, num_variants=5):
    """Generate variants from masked sequence"""
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

def main():
    print("Loading test proteins...")
    proteins = load_test_proteins()

    print("Loading ESM-2 650M...")
    device = torch.device('cuda')
    tokenizer = EsmTokenizer.from_pretrained("facebook/esm2_t33_650M_UR50D")
    model = EsmForMaskedLM.from_pretrained("facebook/esm2_t33_650M_UR50D")
    model = model.to(device)
    model.eval()

    results = {}

    for protein_id, protein_data in proteins.items():
        print(f"\nProcessing {protein_data['name']}...")
        sequence = protein_data['sequence']

        # Generate masked variants at 30% masking
        masked_seq, masked_positions = mask_sequence(sequence, mask_rate=0.3)
        print(f"Masked {len(masked_positions)} positions")

        variants = generate_variants(model, tokenizer, masked_seq, device, num_variants=3)

        results[protein_id] = {
            'original': sequence,
            'masked_sequence': masked_seq,
            'masked_positions': masked_positions,
            'variants': variants,
            'num_variants': len(variants)
        }

        print(f"Generated {len(variants)} variants")
        for i, variant in enumerate(variants):
            identity = sum(1 for a, b in zip(sequence, variant) if a == b) / len(sequence)
            print(f"  Variant {i+1}: {identity:.1%} identity")

    # Save results
    timestamp = int(time.time())
    output_file = f'results/pilot_results_{timestamp}.json'

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()