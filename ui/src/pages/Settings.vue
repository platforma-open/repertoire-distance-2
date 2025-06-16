<script setup lang="ts">
import type { PlRef } from '@platforma-sdk/model';
import { plRefsEqual } from '@platforma-sdk/model';
import { PlDropdownRef, PlMaskIcon16, PlMaskIcon24, PlSlideModal } from '@platforma-sdk/ui-vue';
import { reactive } from 'vue';
import { useApp } from '../app';
import DistanceCard from './DistanceCard.vue';
import './metrics-manager.scss';
import { getMetricLabel } from './util';

const app = useApp();

function setAbundanceRef(abundanceRef?: PlRef) {
  app.model.args.abundanceRef = abundanceRef;
  let label = '';
  if (abundanceRef) {
    label = app.model.outputs.abundanceOptions?.find((o) => plRefsEqual(o.ref, abundanceRef))?.label ?? '';
  }
  app.model.ui.blockTitle = 'Repertoire Distance – ' + label;
}

const settingsAreShown = defineModel<boolean>({ required: true });

const openState = reactive<Record<number, boolean>>({});

const toggleExpandMetric = (index: number) => {
  if (!openState[index]) openState[index] = true;
  else delete openState[index];
};

const deleteMetric = (index: number) => {
  const len = app.model.args.metrics.length;
  app.model.args.metrics.splice(index, 1);
  delete openState[index];
  for (let i = index; i < len - 1; i++) {
    openState[i] = openState[i + 1];
  }
};

const addMetric = () => {
  app.updateArgs((args) => {
    const index = args.metrics.length;
    args.metrics.push({
      type: undefined,
      intersection: 'CDR3ntVJ',
      downsampling: {
        type: 'none',
        valueChooser: 'auto',
      },
    });
    openState[index] = true;
  });
};
</script>

<template>
  <PlSlideModal v-model="settingsAreShown">
    <template #title>Settings</template>
    <PlDropdownRef
      v-model="app.model.args.abundanceRef" :options="app.model.outputs.abundanceOptions ?? []"
      label="Abundance"
      required
      @update:model-value="setAbundanceRef"
    />

    <div class="metrics-manager d-flex flex-column gap-6">
      <div
        v-for="(entry, index) in app.model.args.metrics"
        :key="index"
        :class="{ open: openState[index] ?? false }"
        class="metrics-manager__metric"
      >
        <div
          class="metrics-manager__header d-flex align-center gap-8"
          @click="toggleExpandMetric(index)"
        >
          <div class="metrics-manager__expand-icon">
            <PlMaskIcon16 name="chevron-right" />
          </div>

          <div class="metrics-manager__title flex-grow-1 text-s-btn">
            {{ entry.type ? getMetricLabel(entry.type) : 'New Metric' }}
          </div>

          <div class="metrics-manager__actions">
            <div class="metrics-manager__delete ms-auto" @click.stop="deleteMetric(index)">
              <PlMaskIcon24 name="close" />
            </div>
          </div>
        </div>

        <div class="metrics-manager__content d-flex gap-24 p-24 flex-column">
          <DistanceCard
            v-model="app.model.args.metrics[index]"
          />
        </div>
      </div>

      <div :class="{ 'pt-24': true }" class="metrics-manager__add-action-wrapper">
        <div
          class="metrics-manager__add-btn"
          @click="addMetric"
        >
          <div class="metrics-manager__add-btn-icon">
            <PlMaskIcon16 name="add" />
          </div>
          <div class="metrics-manager__add-btn-title text-s-btn">Add Metric</div>
        </div>
      </div>
    </div>
  </PlSlideModal>
</template>
