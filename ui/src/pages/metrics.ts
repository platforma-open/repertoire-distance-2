import type { MetricUI } from "@platforma-open/milaboratories.repertoire-distance-2.kind";
import { computed } from "vue";
import { useApp } from "../app";

export const useMetrics = () => {
  const app = useApp();
  const metrics = computed({
    get: () => app.model.data.metrics,
    set: (newMetrics: MetricUI[]) => {
      app.model.data.metrics = newMetrics;
    },
  });

  const addMetric = () => {
    metrics.value.push({
      id: `metric-${Date.now()}`,
      type: undefined,
      intersection: undefined,
      downsampling: {
        type: "none",
        valueChooser: "auto",
      },
      isExpanded: true,
    });
  };

  return { metrics, addMetric };
};
