import json
import numpy as np
import pandas as pd
import os
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

def find_latest_screening_results():
    """Find the most recent comprehensive screening results"""
    result_files = [f for f in os.listdir('results/') if f.startswith('comprehensive_screening_')]
    if not result_files:
        raise FileNotFoundError("No comprehensive screening results found! Run screen_all_variants.py first.")

    latest_file = f"results/{sorted(result_files)[-1]}"
    print(f"Analyzing screening results: {latest_file}")
    return latest_file

def extract_analysis_data(screening_results: Dict) -> pd.DataFrame:
    """Extract data into pandas DataFrame for analysis"""
    rows = []

    for protein_id, protein_data in screening_results['proteins'].items():
        for config_id, config_data in protein_data['configurations'].items():
            for variant in config_data['variants']:
                row = {
                    'protein_id': protein_id,
                    'protein_name': protein_data['name'],
                    'protein_family': protein_data['family'],
                    'protein_tier': protein_data['tier'],
                    'masking_strategy': config_data['masking_strategy'],
                    'masking_rate': config_data['masking_rate'],
                    'variant_id': variant['variant_id'],
                    'sequence_identity': variant['sequence_identity'],
                    'evaded': variant['screening'].get('evaded', False),
                    'num_hits': variant['screening'].get('num_hits', 0)
                }

                # Add best hit info if available
                best_hit = variant['screening'].get('best_hit')
                if best_hit:
                    row.update({
                        'best_hit_identity': best_hit['percent_identity'],
                        'best_hit_evalue': best_hit['evalue'],
                        'best_hit_target': best_hit['target_id']
                    })
                else:
                    row.update({
                        'best_hit_identity': None,
                        'best_hit_evalue': None,
                        'best_hit_target': None
                    })

                rows.append(row)

    return pd.DataFrame(rows)

def analyze_evasion_patterns(df: pd.DataFrame) -> Dict:
    """Analyze evasion patterns across different dimensions"""
    print("\n=== Evasion Pattern Analysis ===")

    analysis = {}

    # Overall statistics
    total_variants = len(df)
    total_evaded = df['evaded'].sum()
    overall_rate = total_evaded / total_variants * 100

    analysis['overall'] = {
        'total_variants': total_variants,
        'evaded_variants': total_evaded,
        'evasion_rate': overall_rate
    }

    print(f"Overall: {total_evaded}/{total_variants} ({overall_rate:.1f}%) variants evaded screening")

    # By masking rate
    rate_analysis = df.groupby('masking_rate').agg({
        'evaded': ['count', 'sum', 'mean']
    }).round(3)
    rate_analysis.columns = ['total', 'evaded', 'evasion_rate']

    analysis['by_masking_rate'] = rate_analysis.to_dict('index')

    print(f"\nBy masking rate:")
    for rate, stats in analysis['by_masking_rate'].items():
        print(f"  {rate*100:.0f}%: {stats['evaded']:.0f}/{stats['total']:.0f} ({stats['evasion_rate']*100:.1f}%)")

    # By masking strategy
    strategy_analysis = df.groupby('masking_strategy').agg({
        'evaded': ['count', 'sum', 'mean']
    }).round(3)
    strategy_analysis.columns = ['total', 'evaded', 'evasion_rate']

    analysis['by_strategy'] = strategy_analysis.to_dict('index')

    print(f"\nBy masking strategy:")
    for strategy, stats in analysis['by_strategy'].items():
        print(f"  {strategy}: {stats['evaded']:.0f}/{stats['total']:.0f} ({stats['evasion_rate']*100:.1f}%)")

    # By protein
    protein_analysis = df.groupby(['protein_id', 'protein_family']).agg({
        'evaded': ['count', 'sum', 'mean']
    }).round(3)
    protein_analysis.columns = ['total', 'evaded', 'evasion_rate']

    analysis['by_protein'] = protein_analysis.to_dict('index')

    print(f"\nBy protein:")
    for (protein_id, family), stats in analysis['by_protein'].items():
        print(f"  {protein_id} ({family}): {stats['evaded']:.0f}/{stats['total']:.0f} ({stats['evasion_rate']*100:.1f}%)")

    # By protein family
    family_analysis = df.groupby('protein_family').agg({
        'evaded': ['count', 'sum', 'mean']
    }).round(3)
    family_analysis.columns = ['total', 'evaded', 'evasion_rate']

    analysis['by_family'] = family_analysis.to_dict('index')

    print(f"\nBy protein family:")
    for family, stats in analysis['by_family'].items():
        print(f"  {family}: {stats['evaded']:.0f}/{stats['total']:.0f} ({stats['evasion_rate']*100:.1f}%)")

    return analysis

def analyze_sequence_identity_patterns(df: pd.DataFrame):
    """Analyze sequence identity vs evasion patterns"""
    print(f"\n=== Sequence Identity Analysis ===")

    # Overall identity distribution
    print(f"Sequence identity distribution:")
    print(f"  Mean: {df['sequence_identity'].mean()*100:.1f}%")
    print(f"  Std:  {df['sequence_identity'].std()*100:.1f}%")
    print(f"  Min:  {df['sequence_identity'].min()*100:.1f}%")
    print(f"  Max:  {df['sequence_identity'].max()*100:.1f}%")

    # Identity vs evasion
    evaded_df = df[df['evaded'] == True]
    detected_df = df[df['evaded'] == False]

    if len(evaded_df) > 0:
        print(f"\nEvaded variants identity: {evaded_df['sequence_identity'].mean()*100:.1f}±{evaded_df['sequence_identity'].std()*100:.1f}%")
    if len(detected_df) > 0:
        print(f"Detected variants identity: {detected_df['sequence_identity'].mean()*100:.1f}±{detected_df['sequence_identity'].std()*100:.1f}%")

    # Identity by masking rate
    print(f"\nSequence identity by masking rate:")
    for rate in sorted(df['masking_rate'].unique()):
        rate_df = df[df['masking_rate'] == rate]
        mean_id = rate_df['sequence_identity'].mean() * 100
        std_id = rate_df['sequence_identity'].std() * 100
        print(f"  {rate*100:.0f}%: {mean_id:.1f}±{std_id:.1f}%")

    # Identity by strategy
    print(f"\nSequence identity by masking strategy:")
    for strategy in df['masking_strategy'].unique():
        strategy_df = df[df['masking_strategy'] == strategy]
        mean_id = strategy_df['sequence_identity'].mean() * 100
        std_id = strategy_df['sequence_identity'].std() * 100
        print(f"  {strategy}: {mean_id:.1f}±{std_id:.1f}%")

def analyze_detection_patterns(df: pd.DataFrame):
    """Analyze what gets detected and why"""
    print(f"\n=== Detection Pattern Analysis ===")

    detected_df = df[df['evaded'] == False].copy()

    if len(detected_df) == 0:
        print("No variants were detected - all evaded screening!")
        return

    print(f"Analyzing {len(detected_df)} detected variants...")

    # Detection by similarity threshold
    similarity_bins = [0, 50, 60, 70, 80, 90, 100]
    detected_df['similarity_bin'] = pd.cut(
        detected_df['sequence_identity'] * 100,
        bins=similarity_bins,
        labels=[f"{similarity_bins[i]}-{similarity_bins[i+1]}%" for i in range(len(similarity_bins)-1)]
    )

    print(f"\nDetection by sequence similarity:")
    detection_by_sim = detected_df.groupby('similarity_bin').size()
    for bin_name, count in detection_by_sim.items():
        print(f"  {bin_name}: {count} variants")

    # Best hit analysis
    if 'best_hit_identity' in detected_df.columns:
        print(f"\nBest BLASTP hit statistics:")
        print(f"  Mean identity: {detected_df['best_hit_identity'].mean():.1f}%")
        print(f"  Min identity:  {detected_df['best_hit_identity'].min():.1f}%")
        print(f"  Max identity:  {detected_df['best_hit_identity'].max():.1f}%")

        # Which original proteins are most commonly hit
        print(f"\nMost common BLASTP targets:")
        target_counts = detected_df['best_hit_target'].value_counts()
        for target, count in target_counts.head().items():
            print(f"  {target}: {count} hits")

def create_summary_report(screening_results: Dict, analysis: Dict, df: pd.DataFrame) -> Dict:
    """Create comprehensive summary report"""
    metadata = screening_results['metadata']

    report = {
        'experiment_metadata': {
            'model': 'ESM-2 650M',
            'total_proteins': len(screening_results['proteins']),
            'total_variants': metadata['total_variants_screened'],
            'masking_rates': [0.1, 0.3, 0.5, 0.7],
            'masking_strategies': ['random', 'conservation', 'surface'],
            'variants_per_config': 5,
            'screening_tool': metadata['screening_tool'],
            'evalue_threshold': metadata['evalue_threshold']
        },
        'key_findings': {
            'overall_evasion_rate': analysis['overall']['evasion_rate'],
            'best_strategy': max(analysis['by_strategy'].items(), key=lambda x: x[1]['evasion_rate'])[0],
            'best_masking_rate': max(analysis['by_masking_rate'].items(), key=lambda x: x[1]['evasion_rate'])[0],
            'most_evasive_family': max(analysis['by_family'].items(), key=lambda x: x[1]['evasion_rate'])[0] if analysis['by_family'] else None,
            'mean_sequence_identity': df['sequence_identity'].mean(),
            'identity_vs_evasion_correlation': df['sequence_identity'].corr(df['evaded'].astype(int))
        },
        'detailed_results': analysis
    }

    return report

def main():
    print("=== ProtBreaker Comprehensive Pilot Analysis ===")

    # Load screening results
    results_file = find_latest_screening_results()
    with open(results_file, 'r') as f:
        screening_results = json.load(f)

    # Extract data for analysis
    print("Extracting data for analysis...")
    df = extract_analysis_data(screening_results)
    print(f"Loaded {len(df)} variant records for analysis")

    # Run analyses
    evasion_analysis = analyze_evasion_patterns(df)
    analyze_sequence_identity_patterns(df)
    analyze_detection_patterns(df)

    # Create summary report
    report = create_summary_report(screening_results, evasion_analysis, df)

    # Save analysis results
    timestamp = int(time.time())
    analysis_file = f'results/pilot_analysis_{timestamp}.json'

    with open(analysis_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Analysis Complete ===")
    print(f"Analysis saved to: {analysis_file}")

    # Key insights
    print(f"\n=== KEY INSIGHTS ===")
    print(f"1. Overall evasion rate: {report['key_findings']['overall_evasion_rate']:.1f}%")

    if report['key_findings']['overall_evasion_rate'] > 0:
        print(f"2. Best masking strategy: {report['key_findings']['best_strategy']}")
        print(f"3. Best masking rate: {report['key_findings']['best_masking_rate']*100:.0f}%")
        if report['key_findings']['most_evasive_family']:
            print(f"4. Most evasive protein family: {report['key_findings']['most_evasive_family']}")
    else:
        print("2. No variants evaded screening across all configurations")
        print("3. ESM-2 650M variants maintain sufficient similarity for BLASTP detection")

    print(f"5. Mean sequence identity: {report['key_findings']['mean_sequence_identity']*100:.1f}%")

    corr = report['key_findings']['identity_vs_evasion_correlation']
    if corr is not None:
        print(f"6. Identity-evasion correlation: {corr:.3f}")
        if corr < -0.3:
            print("   → Lower identity variants more likely to evade (expected)")
        elif corr > 0.3:
            print("   → Higher identity variants more likely to evade (unexpected)")
        else:
            print("   → Weak correlation between identity and evasion")

    print(f"\n=== NEXT STEPS ===")
    if report['key_findings']['overall_evasion_rate'] == 0:
        print("• Consider higher masking rates (80-90%) for future experiments")
        print("• Test more advanced models (ESM-2 3B, ESM-3) for potential evasion")
        print("• Implement additional screening tools (HMMER, structure-based)")
    else:
        print("• Investigate why some variants evaded screening")
        print("• Test additional screening tools to confirm evasion")
        print("• Analyze structural properties of evaded variants")

    print("• Expand to full dataset (740 dangerous proteins)")
    print("• Implement iterative refinement attacks")

    return report

if __name__ == "__main__":
    import time
    main()