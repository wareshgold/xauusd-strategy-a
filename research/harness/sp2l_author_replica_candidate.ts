import type { Candle } from '../../src/domain/market/Candle.js';

export type Direction = 'BUY' | 'SELL';

export interface AuthorReplicaConfig {
  readonly pGapPrice: number;
  readonly spikeMultiplier: number;
}

export interface AuthorReplicaSetup {
  readonly direction: Direction;
  readonly setupIndex: number;
  readonly triggerIndex: number;
  readonly entry: number;
  readonly stopLoss: number;
  readonly risk: number;
  readonly takeProfit: number;
}

/**
 * Research-only reproduction of the observable logic in Alireza Sadabadi's
 * SP2L implementation. It is intentionally NOT the canonical Strategy A
 * geometry and must not be used for production decisions.
 *
 * Window convention:
 *   -4 = candle before spike
 *   -3 = spike candle
 *   -2 = candle after spike
 *   -1 = trigger/entry candle
 */
export function detectAuthorReplica(
  candles: readonly Candle[],
  config: AuthorReplicaConfig,
): AuthorReplicaSetup | null {
  if (candles.length < 4) return null;

  const a = candles[candles.length - 4];
  const spike = candles[candles.length - 3];
  const correction = candles[candles.length - 2];
  const trigger = candles[candles.length - 1];

  const buy =
    trigger.low < correction.low &&
    correction.close > spike.close &&
    correction.open > spike.open &&
    spike.close > a.close &&
    spike.open > a.open &&
    correction.close > correction.open &&
    spike.close > spike.open &&
    a.close > a.open &&
    correction.low > a.high + config.pGapPrice &&
    spike.close - spike.open > config.spikeMultiplier * (correction.close - correction.open) &&
    spike.close - spike.open > config.spikeMultiplier * (spike.close - spike.open === 0 ? 0 : spike.close - spike.open) &&
    spike.close - spike.open > config.spikeMultiplier * (trigger.close - trigger.open);

  const sell =
    trigger.high > correction.high &&
    correction.close < spike.close &&
    correction.open < spike.open &&
    spike.close < a.close &&
    spike.open < a.open &&
    correction.close < correction.open &&
    spike.close < spike.open &&
    a.close < a.open &&
    correction.high < a.low - config.pGapPrice &&
    spike.open - spike.close > config.spikeMultiplier * (correction.open - correction.close) &&
    spike.open - spike.close > config.spikeMultiplier * (a.open - a.close) &&
    spike.open - spike.close > config.spikeMultiplier * (trigger.open - trigger.close);

  if (buy === sell) return null;

  if (buy) {
    const stopLoss = a.low;
    const entry = trigger.low;
    const risk = entry - stopLoss;
    return risk > 0 ? {
      direction: 'BUY',
      setupIndex: candles.length - 2,
      triggerIndex: candles.length - 1,
      entry,
      stopLoss,
      risk,
      takeProfit: entry + risk,
    } : null;
  }

  const stopLoss = a.high;
  const entry = trigger.high;
  const risk = stopLoss - entry;
  return risk > 0 ? {
    direction: 'SELL',
    setupIndex: candles.length - 2,
    triggerIndex: candles.length - 1,
    entry,
    stopLoss,
    risk,
    takeProfit: entry - risk,
  } : null;
}
