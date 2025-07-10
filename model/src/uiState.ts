import { randomInt } from '@milaboratories/helpers';
import type { Metric, MetricUI, UiState } from './types';

export const createDefaultUiState = (): UiState => {
  return {
    blockTitle: 'Repertoire Distance',
    graphState: {
      title: 'Repertoire Distance',
      template: 'heatmap',
      currentTab: 'settings',
      layersSettings: {
        heatmapClustered: {
          normalizationDirection: null,
        },
      },
    },
    metrics: createDefaultMetricUis(),
  };
};

export const createDefaultMetricUis = (): MetricUI[] => {
  return [
    {
      id: randomInt(),
      isExpanded: false,
      type: 'F1',
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'hypergeometric',
        valueChooser: 'auto',
      },
    },
    {
      id: randomInt(),
      isExpanded: false,
      type: 'F2',
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'hypergeometric',
        valueChooser: 'auto',
      },
    },
    {
      id: randomInt(),
      isExpanded: false,
      type: 'D',
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'hypergeometric',
        valueChooser: 'auto',
      },
    },
    {
      id: randomInt(),
      isExpanded: false,
      type: 'sharedClonotypes',
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'hypergeometric',
        valueChooser: 'auto',
      },
    },
    {
      id: randomInt(),
      isExpanded: false,
      type: 'correlation',
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'hypergeometric',
        valueChooser: 'auto',
      },
    },
    {
      id: randomInt(),
      isExpanded: false,
      type: 'jaccard',
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'hypergeometric',
        valueChooser: 'auto',
      },
    },
  ];
};

export const convertMetricsUiToArgs = (metrics: MetricUI[]): Metric[] => {
  return metrics.map((metric): Metric => {
    return {
      type: metric.type,
      intersection: metric.intersection,
      downsampling: metric.downsampling,
    };
  });
};

export const convertMetricsArgsToUi = (metrics: Metric[]): MetricUI[] => {
  return metrics.map((metric): MetricUI => {
    return {
      ...metric,
      id: randomInt(),
      isExpanded: false,
    };
  });
}; 