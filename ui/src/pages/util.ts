export const metricTypeOptions = [
  { value: 'F1', label: 'F1 metric' },
  { value: 'F2', label: 'F2 metric' },
  { value: 'D', label: 'D metric' },
  { value: 'sharedClonotypes', label: 'Shared Clonotypes' },
  { value: 'correlation', label: 'Correlation' },
  { value: 'jaccard', label: 'Jaccard' },
];

const labelsMap = (() => {
  const map: Map<string, string> = new Map();
  for (const option of metricTypeOptions) {
    map.set(option.value, option.label);
  }
  return map;
})();
export const getMetricLabel = (value: string) => labelsMap.get(value);
