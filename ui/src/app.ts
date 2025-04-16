import { model } from '@platforma-open/milaboratories.repertoire-distance.model';
import { defineApp } from '@platforma-sdk/ui-vue';
import MainPage from './pages/MainPage.vue';
import DistanceGraph from './pages/DistanceGraph.vue';
export const sdkPlugin = defineApp(model, () => {
  return {
    routes: {
      '/': () => MainPage,
      '/distanceGraph': () => DistanceGraph,
    },
  };
});

export const useApp = sdkPlugin.useApp;
