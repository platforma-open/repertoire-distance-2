<script setup lang="ts">
import type { GraphMakerProps } from '@milaboratories/graph-maker';
import type { PColumnIdAndSpec } from '@platforma-sdk/model';
import { GraphMaker } from '@milaboratories/graph-maker';
import '@milaboratories/graph-maker/styles';
import { ref } from 'vue';
import { useApp } from '../app';

const app = useApp();

function getDefaultOptions(heatmapPCols?: PColumnIdAndSpec[]) {
  if (!heatmapPCols) {
    return undefined;
  }

  function getIndex(name: string, pcols: PColumnIdAndSpec[]): number {
    return pcols.findIndex((p) => p.spec.name === name);
  }

  const defaults: GraphMakerProps['defaultOptions'] = [
    {
      inputName: 'x',
      selectedSource: heatmapPCols[getIndex('pl7.app/vdj/overlap', heatmapPCols)].spec.axesSpec[0],
    },
    {
      inputName: 'y',
      selectedSource: heatmapPCols[getIndex('pl7.app/vdj/overlap', heatmapPCols)].spec.axesSpec[1],
    },
    {
      inputName: 'value',
      selectedSource: heatmapPCols[getIndex('pl7.app/vdj/overlap', heatmapPCols)].spec,
    },
    {
      inputName: 'tabBy',
      selectedSource: heatmapPCols[getIndex('pl7.app/vdj/overlap', heatmapPCols)].spec.axesSpec[2],
    },
  ];

  return defaults;
}

const heatmapPCols = app.model.outputs.heatmapPCols;

const defaultOptions = ref<GraphMakerProps['defaultOptions']>(
  getDefaultOptions(heatmapPCols),
);
</script>

<template>
  <GraphMaker
    v-model="app.model.ui.graphState"
    chart-type="heatmap"
    :p-frame="app.model.outputs.pf"
    :default-options="defaultOptions"
  />
</template>
