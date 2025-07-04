import type { GraphMakerState } from '@milaboratories/graph-maker';
import type { PlDataTableStateV2, PlRef } from '@platforma-sdk/model';

export type DistanceType = 'F1' | 'F2' | 'D' |
  'sharedClonotypes' | 'correlation' | 'jaccard';

export type IntersectionType = 'CDR3ntVJ' | 'CDR3aaVJ' | 'CDR3nt' | 'CDR3aa';

export type Metric = {
  type: DistanceType | undefined;
  intersection: IntersectionType | undefined;
  downsampling: {
    type?: 'none' | 'top' | 'cumtop' | 'hypergeometric';
    valueChooser?: 'min' | 'fixed' | 'max' | 'auto';
    n?: number;
  };
};

export type MetricUI = Metric & {
  id?: number;
  isExpanded?: boolean;
};

export type BlockArgs = {
  abundanceRef?: PlRef;
  metrics: Metric[];
};

export type UiState = {
  blockTitle: string;
  tableState: PlDataTableStateV2;
  graphState: GraphMakerState;
  metrics?: MetricUI[];
}; 