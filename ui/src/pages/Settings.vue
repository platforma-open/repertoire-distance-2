<script setup lang="ts">
import type { PlRef } from '@platforma-sdk/model';
import { plRefsEqual } from '@platforma-sdk/model';
import { PlDropdownRef, PlElementList, PlSlideModal, PlBtnSecondary } from '@platforma-sdk/ui-vue';
import { watch } from 'vue';
import { useApp } from '../app';
import DistanceCard from './DistanceCard.vue';
import './metrics-manager.scss';
import { getMetricLabel } from './util';
import { convertMetricsUiToArgs, convertMetricsArgsToUi } from '../../../model/src/uiState';
import type { MetricUI } from '../../../model/src/types';

const app = useApp();

function setAbundanceRef(abundanceRef?: PlRef) {
  (app.model.args as any).abundanceRef = abundanceRef;
  let label = '';
  if (abundanceRef) {
    label = (app.model.outputs as any).abundanceOptions?.find((o: any) => plRefsEqual(o.ref, abundanceRef))?.label ?? '';
  }
  (app.model.ui as any).blockTitle = 'Repertoire Distance – ' + label;
}

const settingsAreShown = defineModel<boolean>({ required: true });

// Initialize UI state metrics if not present
if (!(app.model.ui as any).metrics) {
  (app.model.ui as any).metrics = convertMetricsArgsToUi((app.model.args as any).metrics);
}

// Sync UI state metrics with args when they change
watch(() => (app.model.ui as any).metrics, (metrics: MetricUI[]) => {
  if (metrics) {
    (app.model.args as any).metrics = convertMetricsUiToArgs(metrics);
  }
}, { deep: true });

// Sync args with UI state when they change externally
watch(() => (app.model.args as any).metrics, (metrics: any[]) => {
  if (metrics && !(app.model.ui as any).metrics) {
    (app.model.ui as any).metrics = convertMetricsArgsToUi(metrics);
  }
}, { deep: true });

const handleExpand = (metric: MetricUI, index: number) => {
  if ((app.model.ui as any).metrics) {
    (app.model.ui as any).metrics[index].isExpanded = !(app.model.ui as any).metrics[index].isExpanded;
  }
};

const handleRemove = (metric: MetricUI, index: number) => {
  if ((app.model.ui as any).metrics) {
    (app.model.ui as any).metrics.splice(index, 1);
  }
  return true; // Allow removal
};

const handleSort = (oldIndex: number, newIndex: number) => {
  if ((app.model.ui as any).metrics) {
    const item = (app.model.ui as any).metrics.splice(oldIndex, 1)[0];
    (app.model.ui as any).metrics.splice(newIndex, 0, item);
  }
  return true; // Allow sorting
};

const addMetric = () => {
  if (!(app.model.ui as any).metrics) {
    (app.model.ui as any).metrics = [];
  }
  
  (app.model.ui as any).metrics.push({
    id: Math.random(),
    isExpanded: true,
    type: undefined,
    intersection: 'CDR3ntVJ',
    downsampling: {
      type: 'none',
      valueChooser: 'auto',
    },
  });
};

const getItemKey = (metric: MetricUI) => metric.id || JSON.stringify(metric);

const isExpanded = (metric: MetricUI) => Boolean(metric.isExpanded);
</script>

<template>
  <PlSlideModal v-model="settingsAreShown">
    <template #title>Settings</template>

    <PlDropdownRef
      v-model="(app.model.args as any).abundanceRef" 
      :options="(app.model.outputs as any).abundanceOptions ?? []"
      label="Abundance"
      required
      @update:model-value="setAbundanceRef"
    />

    <div class="d-flex flex-column gap-6">
      <PlElementList
        v-if="(app.model.ui as any).metrics"
        v-model:items="(app.model.ui as any).metrics"
        :getItemKey="getItemKey"
        :isExpandable="() => true"
        :isExpanded="isExpanded"
        :onExpand="handleExpand"
        :isRemovable="() => true"
        :onRemove="handleRemove"
        :onSort="handleSort"
      >
        <template #item-title="{ item: metric }">
          <div class="text-s-btn">
            {{ metric.type ? getMetricLabel(metric.type) : 'New Metric' }}
          </div>
        </template>

        <template #item-content="{ index }">
          <DistanceCard
            v-model="(app.model.ui as any).metrics[index]"
          />
        </template>
      </PlElementList>
      <PlBtnSecondary icon="add" @click="addMetric">
        Add Metric
      </PlBtnSecondary>
    </div>
  </PlSlideModal>
</template>