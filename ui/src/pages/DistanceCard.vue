<script setup lang="ts">
import type { Metric } from '@platforma-open/milaboratories.repertoire-distance.model';
import type { ListOption } from '@platforma-sdk/ui-vue';
import { PlBtnGroup, PlDropdown, PlNumberField } from '@platforma-sdk/ui-vue';
import './metrics-manager.scss';
import { metricTypeOptions } from './util';

const intersectionOptions: ListOption<string | undefined>[] = [
  { label: 'CDR3nt|V|J', value: 'CDR3ntVJ' },
  { label: 'CDR3aa|V|J', value: 'CDR3aaVJ' },
  { label: 'CDR3nt', value: 'CDR3nt' },
  { label: 'CDR3aa', value: 'CDR3aa' },
];

const downsamplingOptions: ListOption<string | undefined>[] = [
  { label: 'None', value: 'none' },
  { label: 'Top N', value: 'top' },
  { label: 'Cumulative Top', value: 'cumtop' },
  { label: 'Random Sampling', value: 'hypergeometric' },
];

const props = defineModel<Metric>({ 
  required: true,
  default: {
    type: undefined,
    intersection: 'CDR3ntVJ',
    downsampling: {
      type: 'none',
      valueChooser: 'auto',
    },
  }
});
</script>

<template>
  <div class="d-flex flex-column gap-24">
    <PlDropdown
      v-model="props.type" :options="metricTypeOptions"
      label="Type"
      required
    />

    <PlDropdown
      v-model="props.intersection" :options="intersectionOptions"
      label="Intersection"
      required
    />

    <PlDropdown
      v-model="props.downsampling.type" :options="downsamplingOptions"
      label="Downsampling"
      required
    />

    <PlNumberField
      v-if="props.downsampling.type === 'cumtop'"
      v-model="props.downsampling.n"
      label="Select % of the repertoire to include"
      :minValue="0"
      :maxValue="100"
      :step="1"
      required
    />

    <PlNumberField
      v-if="props.downsampling.type === 'top'"
      v-model="props.downsampling.n"
      label="Select Top N"
      :minValue="0"
      required
    />

    <PlBtnGroup
      v-if="props.downsampling.type === 'hypergeometric'"
      v-model="props.downsampling.valueChooser"
      :options="[
        { value: 'fixed', label: 'Fixed' },
        { value: 'min', label: 'Min' },
        { value: 'auto', label: 'Auto' },
        { value: 'max', label: 'Max' },
      ]"
    />

    <PlNumberField
      v-if="props.downsampling.valueChooser === 'fixed'"
      v-model="props.downsampling.n"
      label="Select N"
      :minValue="0"
      required
    />
  </div>
</template>

<style lang="scss" scoped>
.downsampling-section {
  border: 1px solid var(--border-color-div-grey);
  border-radius: 6px;
  overflow: hidden;
  background-color: var(--bg-base-light);
  transition: all 0.2s ease-in-out;

  &:hover {
    border-color: var(--border-color-focus);
  }
}

.downsampling-header {
  padding: 16px;
  background: linear-gradient(180deg, #EBFFEB 0%, #FFF 100%);
}

.downsampling-content {
  max-height: 0;
  overflow: hidden;
  transition: all 0.2s ease-in-out;
  opacity: 0;

  &.is-visible {
    max-height: 500px;
    opacity: 1;
    padding: 16px;
  }
}

.downsampling-option {
  .option-label {
    font-weight: 600;
    margin-bottom: 4px;
  }

  .option-description {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-bottom: 16px;
  }
}

.mt-16 {
  margin-top: 16px;
}
</style>

<!-- @click="removeMetric(index)" -->
