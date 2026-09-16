import type { Candle } from '../../src/domain/market/Candle.ts';
import { runStrategyABacktest, type StrategyABacktestRun, type StrategyADecision } from '../../src/backtest/StrategyAAdapter.ts';
import type { Sp2lGeometryContract } from './sp2l_geometry_contract_v1';
import { assertCanonicalGeometryFrozen } from './sp2l_geometry_contract_v1';

/**
 * Research-only integration boundary.
 *
 * This wrapper does not define SP2L geometry and does not generate BUY/SELL
 * decisions. It only prevents a caller from treating an unresolved geometry
 * contract as canonical backtest input.
 */
export function runFrozenGeometryBacktest(
  candles: readonly Candle[],
  geometry: Sp2lGeometryContract,
  decide: StrategyADecision,
): StrategyABacktestRun {
  assertCanonicalGeometryFrozen(geometry);
  return runStrategyABacktest(candles, decide);
}
