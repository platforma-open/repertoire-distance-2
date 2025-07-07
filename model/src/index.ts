import type { GraphMakerState } from '@milaboratories/graph-maker';
import type { InferOutputsType, PColumnIdAndSpec, PlDataTableStateV2, PlRef } from '@platforma-sdk/model';
import { BlockModel, createPFrameForGraphs, createPlDataTableV2 } from '@platforma-sdk/model';

export type DistanceType = 'F1' | 'F2' | 'D' |
  'sharedClonotypes' | 'correlation' | 'jaccard';

export type IntersectionType = 'CDR3ntVJ' | 'CDR3aaVJ' | 'CDR3nt' | 'CDR3aa';

export type Metric = {
  type: DistanceType | undefined;
  intersection: IntersectionType | undefined;
};

export type BlockArgs = {
  abundanceRef?: PlRef;
  metrics: Metric[];
};

export type UiState = {
  blockTitle: string;
  tableState?: PlDataTableStateV2;
  graphState: GraphMakerState;
};

export const model = BlockModel.create()

  .withArgs<BlockArgs>({
    metrics: [
      {
        type: 'F1',
        intersection: 'CDR3ntVJ',
      },
      {
        type: 'F2',
        intersection: 'CDR3ntVJ',
      },
      {
        type: 'D',
        intersection: 'CDR3ntVJ',
      },
      {
        type: 'sharedClonotypes',
        intersection: 'CDR3ntVJ',
      },
      {
        type: 'correlation',
        intersection: 'CDR3ntVJ',
      },
      {
        type: 'jaccard',
        intersection: 'CDR3ntVJ',
      },
    ],
  })

  .withUiState<UiState>({
    blockTitle: 'Repertoire Distance 2',
    graphState: {
      title: 'Repertoire Distance 2',
      template: 'heatmap',
      currentTab: null,
    },

    tableState: {
      gridState: {},
      pTableParams: {
        sorting: [],
        filters: [],
      },
    },
  })

  .argsValid((ctx) => ctx.args.abundanceRef !== undefined)

  .output('abundanceOptions', (ctx) =>
    ctx.resultPool.getOptions([{
      axes: [
        { name: 'pl7.app/sampleId' },
        { },
      ],
      annotations: {
        'pl7.app/isAbundance': 'true',
        'pl7.app/abundance/normalized': 'false',
        'pl7.app/abundance/isPrimary': 'true',
      },
    },
    ], { includeNativeLabel: true }),
  )

  .output('pt', (ctx) => {
    const pCols = ctx.outputs?.resolve('pfUnique')?.getPColumns();
    if (pCols === undefined) {
      return undefined;
    }
    const inputOptions = ctx.resultPool.getOptions([
      {
        axes: [
          { name: 'pl7.app/sampleId' },
          {},
        ],
        annotations: {
          'pl7.app/isAbundance': 'true',
          'pl7.app/abundance/normalized': 'false',
          'pl7.app/abundance/isPrimary': 'true',
        },
      },
    ]);
    const allowedSampleIds = inputOptions.map((opt) => opt.ref?.name || opt.ref);
    const filteredPCols = pCols.filter((col) => allowedSampleIds.includes(col.id));
    return createPlDataTableV2(ctx, filteredPCols, ctx.uiState?.tableState ?? {
      gridState: {},
      pTableParams: {
        sorting: [],
        filters: [],
      },
    });
  })

  .output('pf', (ctx) => {
    const pCols = ctx.outputs?.resolve('pf')?.getPColumns();
    if (pCols === undefined) {
      return undefined;
    }

    return createPFrameForGraphs(ctx, pCols);
  })

  .output('heatmapPCols', (ctx) => {
    const pCols = ctx.outputs?.resolve('pf')?.getPColumns();
    if (pCols === undefined) {
      return undefined;
    }

    return pCols.map(
      (c) =>
        ({
          columnId: c.id,
          spec: c.spec,
        } satisfies PColumnIdAndSpec),
    );
  })

  .output('isRunning', (ctx) => ctx.outputs?.getIsReadyOrError() === false)

  .title((ctx) => ctx.uiState?.blockTitle ?? 'Repertoire Distance')

  .sections((_) => [
    { type: 'link', href: '/', label: 'Main' },
    { type: 'link', href: '/distanceGraph', label: 'Distance Graph' },
  ])

  .done();

export type BlockOutputs = InferOutputsType<typeof model>;
