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
 * Research-only reproduction of observable logic in Alireza Sadabadi's
 * SP2L implementation. It is NOT canonical Strategy A geometry.
 *
 * Window convention:
 *   -4 = candle before spike
 *   -3 = spike candle
 *   -2 = candle after spike
 *   -1 = current/trigger candle
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
  if (!a || !spike || !correction || !trigger) return null;

  const spikeBodyBuy = spike.close - spike.open;
  const spikeBodySell = spike.open - spike.close;

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
    spikeBodyBuy > config.spikeMultiplier * (correction.close - correction.open) &&
    spikeBodyBuy > config.spikeMultiplier * (a.close - a.open) &&
    spikeBodyBuy > config.spikeMultiplier * (trigger.close - trigger.open);

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
    spikeBodySell > config.spikeMultiplier * (correction.open - correction.close) &&
    spikeBodySell > config.spikeMultiplier * (a.open - a.close) &&
    spikeBodySell > config.spikeMultiplier * (trigger.open - trigger.close);

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
