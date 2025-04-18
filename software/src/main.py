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
        sampled_counts = rng.multivariate_hypergeometric(counts, min_reads) if sid in samples_above else counts
        sample_df = sample_df.copy()
        sample_df['numberOfreads'] = sampled_counts
        downsampled.append(sample_df)

    df_down = pd.concat(downsampled, ignore_index=True)
    df_down['fractionOfReads'] = df_down.groupby('sampleId')['numberOfreads'].transform(lambda x: x / x.sum())
    return df_down

# ---------- Clone Key Builder ----------
def make_clone_key(row, intersection_type):
    if intersection_type == 'CDR3ntVJ':
        return f"{row['CDR3nt']}|{row['VGene']}|{row['JGene']}"
    elif intersection_type == 'CDR3aaVJ':
        return f"{row['CDR3aa']}|{row['VGene']}|{row['JGene']}"
    elif intersection_type == 'CDR3nt':
        return row['CDR3nt']
    elif intersection_type == 'CDR3aa':
        return row['CDR3aa']
    else:
        raise ValueError(f"Unsupported intersection_type: {intersection_type}")

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
        return len(shared) / (len(set1) * len(set2))
    elif metric == 'correlation':
        return linregress(f1, f2).rvalue if len(shared) > 1 else 0.0
    elif metric == 'sharedClonotypes':
        return len(shared)
    else:
        raise ValueError(f"Unsupported metric: {metric}")

# ---------- Main Processing ----------
def compute_metrics_wide(df_down, metric_configs):
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
        df['cloneKey'] = df.apply(lambda row: make_clone_key(row, intersection), axis=1)
        df = df[['sampleId', 'cloneKey', 'fractionOfReads']].rename(columns={'fractionOfReads': 'cloneFraction'})

        sample_clone_dict = {
            sid: g.set_index('cloneKey')['cloneFraction'].to_dict()
            for sid, g in df.groupby('sampleId')
        }
        sample_cloneset_dict = {sid: set(clones.keys()) for sid, clones in sample_clone_dict.items()}

        for sid in sample_ids:
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
    parser = argparse.ArgumentParser(description="Downsample and compute wide-format clonotype distances between samples.")
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
    df.rename(columns={
        'CDR3aa': 'CDR3aa',
        'CDR3nt': 'CDR3nt',
        'count': 'numberOfreads'
    }, inplace=True)

    required_cols = {'sampleId', 'numberOfreads', 'CDR3aa', 'CDR3nt', 'VGene', 'JGene'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Missing required columns: {required_cols - set(df.columns)}")

    # Load metric config JSON
    with open(args.json, 'r') as f:
        metric_configs = json.load(f)

    df_downsampled = downsample_df(df)
    full_result_df = compute_metrics_wide(df_downsampled, metric_configs)

    # Save full version
    full_result_df.to_csv(args.output_full, index=False, sep='\t')

    # Deduplicate: keep only (sample1 <= sample2)
    unique_result_df = full_result_df[
        full_result_df['sample1'] <= full_result_df['sample2']
    ].copy()
    unique_result_df.to_csv(args.output_unique, index=False, sep='\t')


if __name__ == '__main__':
    main()
