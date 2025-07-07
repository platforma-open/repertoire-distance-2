<script setup lang="ts">
import type { PlDataTableStateV2 } from '@platforma-sdk/model';
import { PlAgDataTableV2, PlBlockPage, PlBtnGhost, PlEditableTitle, PlMaskIcon24, usePlDataTableSettingsV2 } from '@platforma-sdk/ui-vue';
import { computed, ref } from 'vue';
import { useApp } from '../app';
import SettingsModal from './Settings.vue';

const app = useApp();

const tableSettings = usePlDataTableSettingsV2({
  model: () => app.model.outputs.pt,
});

const tableLoadingText = computed(() => {
  if (app.model.outputs.isRunning) {
    return 'Running';
  }
  return 'Loading';
});

const settingsAreShown = ref((app.model.args as { abundanceRef?: unknown }).abundanceRef !== undefined);
const showSettings = () => {
  settingsAreShown.value = true;
};

const blockTitle = computed({
  get: () => (app.model.ui as { blockTitle: string }).blockTitle,
  set: (value: string) => { (app.model.ui as { blockTitle: string }).blockTitle = value; },
});

const tableState = computed({
  get: () => (app.model.ui as { tableState: PlDataTableStateV2 }).tableState,
  set: (value: PlDataTableStateV2) => { (app.model.ui as { tableState: PlDataTableStateV2 }).tableState = value; },
});

</script>

<template>
  <PlBlockPage>
    <template #title>
      <PlEditableTitle v-model="blockTitle" max-width="600px" :max-length="40" />
    </template>
    <template #append>
      <PlBtnGhost @click.stop="showSettings">
        Settings
        <template #append>
          <PlMaskIcon24 name="settings" />
        </template>
      </PlBtnGhost>
    </template>
    <PlAgDataTableV2
      v-model="tableState"
      :settings="tableSettings"
      show-columns-panel
      show-export-button
      :loading-text="tableLoadingText"
      not-ready-text="Data is not computed"
    />
  </PlBlockPage>

  <SettingsModal v-model="settingsAreShown" />
</template>