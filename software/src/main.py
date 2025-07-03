import numpy as np
import pandas as pd
import argparse
import json
from collections import defaultdict
from itertools import combinations_with_replacement, product
from scipy.stats import linregress
from numpy.random import default_rng

# ---------- Downsampling ----------
def downsample_df(df):
    total_reads = df.groupby('sampleId')['numberOfreads'].sum()
    q20 = np.quantile(total_reads, 0.2)
    threshold = 0.5 * q20
    samples_above = total_reads[total_reads > threshold].index
    min_reads = total_reads.loc[samples_above].min() if len(samples_above) > 0 else 0

    rng = default_rng(12345)
    downsampled = []
    for sid in df['sampleId'].unique():
        sample_df = df[df['sampleId'] == sid]
        counts = sample_df['numberOfreads'].values
        
        current_sample_total_reads = counts.sum()
        
        # Determine actual number of reads to sample
        # If sample is above threshold, downsample to min_reads (but not more than current total)
        # If sample is not above threshold, or min_reads is 0, or current total is 0, keep original counts
        if sid in samples_above and min_reads > 0 and current_sample_total_reads > 0:
            actual_reads_to_sample = min(min_reads, current_sample_total_reads)
            sampled_counts = rng.multivariate_hypergeometric(counts, actual_reads_to_sample)
        else:
            sampled_counts = counts

        sample_df = sample_df.copy()
        sample_df['numberOfreads'] = sampled_counts
        downsampled.append(sample_df)

    df_down = pd.concat(downsampled, ignore_index=True)
    
    # Recalculate fractionOfReads ensuring no division by zero for samples with 0 reads post-downsampling
    df_down['fractionOfReads'] = df_down.groupby('sampleId')['numberOfreads'].transform(
        lambda x: x / x.sum() if x.sum() > 0 else 0
    )
    return df_down

# ---------- Clone Key Builder ----------
def make_clone_key(row, intersection_type, is_single_cell_data):
    if is_single_cell_data:
        # Single-cell data: always use both chains for these intersection types
        if intersection_type == 'CDR3ntVJ':
            return f"{row['CDR3nt_A']}|{row['CDR3nt_B']}|{row['VGene_A']}|{row['VGene_B']}|{row['JGene_A']}|{row['JGene_B']}"
        elif intersection_type == 'CDR3aaVJ':
            return f"{row['CDR3aa_A']}|{row['CDR3aa_B']}|{row['VGene_A']}|{row['VGene_B']}|{row['JGene_A']}|{row['JGene_B']}"
        elif intersection_type == 'CDR3nt':
            return f"{row['CDR3nt_A']}|{row['CDR3nt_B']}"
        elif intersection_type == 'CDR3aa':
            return f"{row['CDR3aa_A']}|{row['CDR3aa_B']}"
        else:
            raise ValueError(f"Unsupported intersection_type for single-cell data: {intersection_type}")
    else:
        # Bulk data: use single-chain columns
        if intersection_type == 'CDR3ntVJ':
            return f"{row['CDR3nt']}|{row['VGene']}|{row['JGene']}"
        elif intersection_type == 'CDR3aaVJ':
            return f"{row['CDR3aa']}|{row['VGene']}|{row['JGene']}"
        elif intersection_type == 'CDR3nt':
            return row['CDR3nt']
        elif intersection_type == 'CDR3aa':
            return row['CDR3aa']
        else:
            raise ValueError(f"Unsupported intersection_type for bulk data: {intersection_type}")

# ---------- Metric Calculation ----------
def compute_metric(s1, s2, clones1, clones2, set1, set2, metric):
    if s1 == s2:
        # Self-pair → perfect match
        if metric in ['F1', 'F2', 'jaccard', 'correlation', 'D']:
            return 1.0
        elif metric == 'sharedClonotypes':
            return len(set1)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

    shared = set1 & set2
    if len(shared) == 0:
        return 0.0

    f1 = np.array([clones1[k] for k in shared])
    f2 = np.array([clones2[k] for k in shared])

    if metric == 'F1':
        return np.sqrt(f1.sum() * f2.sum())
    elif metric == 'F2':
        return np.sqrt(f1 * f2).sum()
    elif metric == 'jaccard':
        return len(shared) / len(set1 | set2)
    elif metric == 'D':
        # This D metric is defined as |intersection| / (|set1| * |set2|)
        return len(shared) / (len(set1) * len(set2))
    elif metric == 'correlation':
        # Ensure there's enough data for correlation (at least 2 shared clonotypes)
        # and that there is variance in the shared fractions
        if len(shared) > 1 and np.std(f1) > 0 and np.std(f2) > 0:
            return linregress(f1, f2).rvalue
        else:
            return 0.0
    elif metric == 'sharedClonotypes':
        return len(shared)
    else:
        raise ValueError(f"Unsupported metric: {metric}")

# ---------- Main Processing ----------
def compute_metrics_wide(df_down, metric_configs, is_single_cell_data):
    sample_ids = sorted(df_down['sampleId'].unique())

    # All sample × sample pairs
    all_output_pairs = list(product(sample_ids, repeat=2))
    unique_pairs = list(combinations_with_replacement(sample_ids, 2))

    # Group metrics by intersection type
    metrics_by_intersection = defaultdict(list)
    for config in metric_configs:
        metrics_by_intersection[config['intersection']].append(config['type'])

    results = {}

    for intersection, metric_list in metrics_by_intersection.items():
        # Step 1: build cloneKey once
        df = df_down.copy()
        df['cloneKey'] = df.apply(lambda row: make_clone_key(row, intersection, is_single_cell_data), axis=1)
        df = df[['sampleId', 'cloneKey', 'fractionOfReads']].rename(columns={'fractionOfReads': 'cloneFraction'})

        sample_clone_dict = {
            sid: g.set_index('cloneKey')['cloneFraction'].to_dict()
            for sid, g in df.groupby('sampleId')
        }
        sample_cloneset_dict = {sid: set(clones.keys()) for sid, clones in sample_clone_dict.items()}

        for sid in sample_ids:
            # Ensure all sample_ids are present in dictionaries, even if they have no clones
            sample_clone_dict.setdefault(sid, {})
            sample_cloneset_dict.setdefault(sid, set())

        # Step 2: compute each metric only once per unique unordered pair
        metric_values = {metric: {} for metric in metric_list}

        for s1, s2 in unique_pairs:
            c1, c2 = sample_clone_dict[s1], sample_clone_dict[s2]
            set1, set2 = sample_cloneset_dict[s1], sample_cloneset_dict[s2]

            for metric in metric_list:
                val = compute_metric(s1, s2, c1, c2, set1, set2, metric)
                metric_values[metric][(s1, s2)] = val
                if s1 != s2:
                    metric_values[metric][(s2, s1)] = val

        # Step 3: populate results
        for s1, s2 in all_output_pairs:
            key = (s1, s2)
            if key not in results:
                results[key] = {'sample1': s1, 'sample2': s2}
            for metric in metric_list:
                metric_col = f"{metric}_{intersection}"
                results[key][metric_col] = metric_values[metric].get((s1, s2), 0.0)

    return pd.DataFrame(results.values())


# ---------- CLI Entry ----------
def main():
    parser = argparse.ArgumentParser(description="Downsample and compute wide-format clonotype distances between samples, supporting both bulk and single-cell dual-chain data.")
    parser.add_argument('-i', '--input', required=True, help="Input TSV or CSV file")
    parser.add_argument('-j', '--json', required=True, help="JSON config: [{intersection: ..., type: ...}]")
    parser.add_argument('-o1', '--output_full', required=True, help="Output CSV file with all sample pairs (matrix-friendly)")
    parser.add_argument('-o2', '--output_unique', required=True, help="Output CSV file with unique sample pairs only")
    parser.add_argument('--sep', default=None, help="Field separator (default auto-detect: CSV=',' or TSV='\\t')")

    args = parser.parse_args()
    sep = args.sep or ('\t' if args.input.endswith('.tsv') else ',')

    df = pd.read_csv(args.input, sep=sep)

    # Clean and normalize column names
    df.columns = [col.strip().replace('"', '').replace(' ', '') for col in df.columns]
    
    # Attempt to detect if it's single-cell dual-chain data based on column presence
    # Prioritize 'B' chain columns for detection as they distinguish single-cell
    single_cell_cols_present = {
        'CDR3aaB', 'CDR3ntB', 'VGeneB', 'JGeneB'
    }.issubset(df.columns)

    is_single_cell_data = False
    if single_cell_cols_present:
        is_single_cell_data = True
        # Rename single-cell columns to standardized internal names (_A, _B suffix)
        df.rename(columns={
            'CDR3aaA': 'CDR3aa_A', 'CDR3ntA': 'CDR3nt_A', 'VGeneA': 'VGene_A', 'JGeneA': 'JGene_A',
            'CDR3aaB': 'CDR3aa_B', 'CDR3ntB': 'CDR3nt_B', 'VGeneB': 'VGene_B', 'JGeneB': 'JGene_B',
            'count': 'numberOfreads'
        }, inplace=True)
        # Ensure all required A and B chain columns are present
        required_cols = {
            'sampleId', 'numberOfreads',
            'CDR3aa_A', 'CDR3nt_A', 'VGene_A', 'JGene_A',
            'CDR3aa_B', 'CDR3nt_B', 'VGene_B', 'JGene_B'
        }
    else:
        # Assume bulk data, rename original columns
        df.rename(columns={
            'CDR3aa': 'CDR3aa', # No change, but good to list for clarity
            'CDR3nt': 'CDR3nt', # No change
            'count': 'numberOfreads',
            'VGene': 'VGene', # No change
            'JGene': 'JGene' # No change
        }, inplace=True)
        # Ensure all required bulk columns are present
        required_cols = {'sampleId', 'numberOfreads', 'CDR3aa', 'CDR3nt', 'VGene', 'JGene'}

    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns. Expected for data type detected: {required_cols - set(df.columns)}")

    # Load metric config JSON
    with open(args.json, 'r') as f:
        metric_configs = json.load(f)

    df_downsampled = downsample_df(df)
    full_result_df = compute_metrics_wide(df_downsampled, metric_configs, is_single_cell_data)

    # Save full version
    full_result_df.to_csv(args.output_full, index=False, sep='\t')

    # Deduplicate: keep only (sample1 <= sample2)
    unique_result_df = full_result_df[
        full_result_df['sample1'] <= full_result_df['sample2']
    ].copy()
    unique_result_df.to_csv(args.output_unique, index=False, sep='\t')


if __name__ == '__main__':
    main()