<script setup lang="ts">
import type { PlDataTableSettings } from '@platforma-sdk/ui-vue';
import { PlAgDataTable, PlAgDataTableToolsPanel, PlBlockPage, PlBtnGhost, PlEditableTitle, PlMaskIcon24 } from '@platforma-sdk/ui-vue';
import { computed, ref } from 'vue';
import { useApp } from '../app';
import SettingsModal from './Settings.vue';

const app = useApp();

const tableSettings = computed<PlDataTableSettings>(() => ({
  sourceType: 'ptable',
  pTable: app.model.outputs.pt,
}));

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
    <PlAgDataTable v-model="app.model.ui.tableState" :settings="tableSettings" show-columns-panel show-export-button />
  </PlBlockPage>

  <SettingsModal v-model="settingsAreShown" />
</template>