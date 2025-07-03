<script setup lang="ts">
import type { PlDataTableSettingsV2 } from '@platforma-sdk/ui-vue';
import { PlAgDataTableV2, PlAgDataTableToolsPanel, PlBlockPage, PlBtnGhost, PlEditableTitle, PlMaskIcon24 } from '@platforma-sdk/ui-vue';
import { computed, ref } from 'vue';
import { useApp } from '../app';
import SettingsModal from './Settings.vue';
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
    <div v-if="app.model.outputs.pt && !app.model.outputs.isRunning" style="flex: 1;">
      <PlAgDataTableV2
        v-model="app.model.ui.tableState"
        :settings="tableSettings as PlDataTableSettingsV2"
        show-columns-panel
        show-export-button
      />
    </div>
    <div v-else style="flex: 1; display: flex; align-items: center; justify-content: center; min-height: 200px;">
      <span v-if="app.model.outputs.isRunning">Processing... Please wait.</span>
      <span v-else>Press Run to start analysis.</span>
    </div>
  </PlBlockPage>

  <SettingsModal v-model="settingsAreShown" />
</template>