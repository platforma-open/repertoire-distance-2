import type { InferOutputsType, PColumnIdAndSpec, PColumnSpec } from '@platforma-sdk/model';
import { BlockModel, createPFrameForGraphs, createPlDataTableV2, isPColumnSpec } from '@platforma-sdk/model';
import type { BlockArgs, UiState } from './types';
import { createDefaultUiState, convertMetricsUiToArgs } from './uiState';

export * from './types';
export * from './uiState';

function isNumericType(c: PColumnSpec): boolean {
  return c.valueType === 'Double' || c.valueType === 'Int' || c.valueType === 'Float' || c.valueType === 'Long';
}

export const model = BlockModel.create()
  .withArgs<BlockArgs>({
    metrics: convertMetricsUiToArgs(createDefaultUiState().metrics!),
  })

  .withUiState<UiState>(createDefaultUiState())

  .argsValid((ctx) => ctx.args.abundanceRef !== undefined)

  .output('abundanceOptions', (ctx) =>
    ctx.resultPool.getOptions((c) =>
      isPColumnSpec(c) && isNumericType(c)
      && c.annotations?.['pl7.app/isAbundance'] === 'true'
      && c.annotations?.['pl7.app/abundance/normalized'] === 'false'
      && c.annotations?.['pl7.app/abundance/isPrimary'] === 'true',
    ))

  .output('pt', (ctx) => {
    const pCols = ctx.outputs?.resolve('pfUnique')?.getPColumns();
    if (pCols === undefined) {
      return undefined;
    }

    return createPlDataTableV2(ctx, pCols, ctx.uiState.tableState);
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
