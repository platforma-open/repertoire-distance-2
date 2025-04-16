import type { GraphMakerState } from '@milaboratories/graph-maker';
import type { InferOutputsType, PColumnIdAndSpec, PColumnSpec, PlDataTableState, PlRef, RenderCtx } from '@platforma-sdk/model';
import { BlockModel, createPFrameForGraphs, createPlDataTable, isPColumnSpec, getUniquePartitionKeys } from '@platforma-sdk/model';

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
  tableState?: PlDataTableState;
  graphState: GraphMakerState;
};

function isNumericType(c: PColumnSpec): boolean {
  return c.valueType === 'Double' || c.valueType === 'Int' || c.valueType === 'Float' || c.valueType === 'Long';
}

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
    blockTitle: 'Repertoire Distance',
    graphState: {
      title: 'Repertoire Distance',
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
    ctx.resultPool.getOptions((c) =>
      isPColumnSpec(c) && isNumericType(c)
      && c.annotations?.['pl7.app/isAbundance'] === 'true'
      && c.annotations?.['pl7.app/abundance/normalized'] === 'false',
    ))

  .output('pt', (ctx) => {
    const pCols = ctx.outputs?.resolve('pfUnique')?.getPColumns();
    if (pCols === undefined) {
      return undefined;
    }

    return createPlDataTable(ctx, pCols, ctx.uiState?.tableState);
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
