<script setup lang="ts">
import type { PlAgDataTableSettings } from '@platforma-sdk/ui-vue';
import { PlAgDataTableV2, PlAgDataTableToolsPanel, PlBlockPage, PlBtnGhost, PlEditableTitle, PlMaskIcon24 } from '@platforma-sdk/ui-vue';
import { computed, ref } from 'vue';
import { useApp } from '../app';
import SettingsModal from './Settings.vue';

const app = useApp();

const tableSettings = computed<PlAgDataTableSettings>(() => {
  const pTable = app.model.outputs.pt;
  if (pTable === undefined && !app.model.outputs.isRunning) {
    // special case: when block is not yet started at all (no table calculated)
    return undefined;
  }
  return {
    sourceType: 'ptable',
    model: pTable,
  };
});

const settingsAreShown = ref(app.model.args.abundanceRef !== undefined);
const showSettings = () => {
  settingsAreShown.value = true;
};

</script>

<template>
  <PlBlockPage>
    <template #title>
      <PlEditableTitle v-model="app.model.ui.blockTitle" max-width="600px" :max-length="40" />
    </template>
    <template #append>
      <PlAgDataTableToolsPanel />

      <PlBtnGhost @click.stop="showSettings">
        Settings
        <template #append>
          <PlMaskIcon24 name="settings" />
        </template>
      </PlBtnGhost>
    </template>
    <PlAgDataTableV2 v-model="app.model.ui.tableState" :settings="tableSettings" show-columns-panel show-export-button />
  </PlBlockPage>

  <SettingsModal v-model="settingsAreShown" />
</template>