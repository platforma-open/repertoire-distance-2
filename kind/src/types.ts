/**
 * The distance-metric vocabulary. It lives in the kind because the kind's
 * init-params contract names these types, and a kind cannot import from the
 * model (the model depends on the kind, not the other way round).
 */

export type DistanceType = "F1" | "F2" | "D" | "sharedClonotypes" | "correlation" | "jaccard";

/**
 * The sequence region a pair of repertoires is intersected on. The `VJ`
 * variants also require matching V and J genes, so they do not apply to
 * peptide inputs, which carry no genes.
 */
export type IntersectionType = "CDR3ntVJ" | "CDR3aaVJ" | "CDR3nt" | "CDR3aa";

/** One distance measurement. Every field of it reaches the workflow. */
export type Metric = {
  id: string;
  type: DistanceType | undefined;
  intersection: IntersectionType | undefined;
  downsampling: {
    type?: "none" | "top" | "cumtop" | "hypergeometric";
    valueChooser?: "min" | "fixed" | "max" | "auto";
    n?: number;
  };
};

/** What the input holds: VDJ clonotypes, or peptide variants with no V/J genes. */
export type Modality = "antibody_tcr" | "peptide";

/** One editable row: a metric plus the disclosure state the editor keeps. */
export type MetricUI = Metric & {
  isExpanded?: boolean;
};

export const DISTANCE_TYPES: readonly DistanceType[] = [
  "F1",
  "F2",
  "D",
  "sharedClonotypes",
  "correlation",
  "jaccard",
];

export const INTERSECTION_TYPES: readonly IntersectionType[] = [
  "CDR3ntVJ",
  "CDR3aaVJ",
  "CDR3nt",
  "CDR3aa",
];

export const MODALITIES: readonly string[] = ["antibody_tcr", "peptide"];

export const DOWNSAMPLING_TYPES: readonly string[] = ["none", "top", "cumtop", "hypergeometric"];
export const VALUE_CHOOSERS: readonly string[] = ["min", "fixed", "max", "auto"];
