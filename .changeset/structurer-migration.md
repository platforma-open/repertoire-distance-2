---
"@platforma-open/milaboratories.repertoire-distance-2": minor
"@platforma-open/milaboratories.repertoire-distance-2.model": minor
"@platforma-open/milaboratories.repertoire-distance-2.ui": minor
"@platforma-open/milaboratories.repertoire-distance-2.workflow": minor
"@platforma-open/milaboratories.repertoire-distance-2.software": patch
---

Migrate onto the latest block-tools structurer layout, add the mandatory block
kind, and bump the SDK to latest (model 1.83.0, ui-vue 1.83.3, workflow-tengo
6.8.3, tengo-builder 4.0.23, block-tools 2.14.3).

The kind's init-params contract is the abundance column, the metric rows (with
the input modality they were written for) and the block subtitle, so a project
template can seed a configured Distance Analysis block. Applying one also
restores the subtitle now: the settings page snapshots the dataset label from
the options when the block arrives with an input already chosen.

The metric vocabulary (`DistanceType`, `IntersectionType`, `Metric`) moved into
the kind package, which the model and UI import from. The persisted shape is
unchanged and the model was already on BlockModelV3.

The side of the pair each sample axis stands for moved from its `domain` to its
`contextDomain`, so both axes stay equal to the plain `pl7.app/sampleId` other
blocks emit and sample metadata can reach the heatmap. The model folds the
marker back into `domain` when it builds the PFrame, where axes are joined by
exact domain and the two sides must stay apart.
