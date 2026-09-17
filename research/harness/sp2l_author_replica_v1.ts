import type { Candle } from '../src/domain/market/Candle.ts';

export interface AuthorReplicaConfig {
  readonly gapPrice: number;
  readonly spikeMultiplier: number;
  readonly maxSlDistance: number;
  readonly tpR: number;
}

export interface AuthorReplicaSetup {
  readonly direction: 'BUY' | 'SELL';
  readonly setupIndex: number;
  readonly entryIndex: number;
  readonly entry: number;
  readonly stopLoss: number;
  readonly tp1: number;
  readonly risk: number;
  readonly pGapDistance: number;
}

/**
 * Research-only reconstruction of the author-owned SP2L implementation.
 * This is deliberately NOT the canonical Strategy A geometry.
 *
 * Four-candle indexing follows the author code:
 *   -4 previous candle, -3 spike, -2 post-spike/correction, -1 current.
 */
export const DEFAULT_AUTHOR_REPLICA: AuthorReplicaConfig = {
  gapPrice: 1.0,
  spikeMultiplier: 1.5,
  maxSlDistance: 10.0,
  tpR: 1.0,
};

function bullishSetup(data: readonly Candle[], i: number, c: AuthorReplicaConfig): boolean {
  if (i < 4) return false;
  const m4 = data[i - 4]!;
  const m3 = data[i - 3]!;
  const m2 = data[i - 2]!;
  const m1 = data[i]!;
  return (
    m1.low < m2.low &&
    m2.close > m3.close &&
    m2.open > m3.open &&
    m3.close > m4.close &&
    m3.open > m4.open &&
    m2.close > m2.open &&
    m3.close > m3.open &&
    m4.close > m4.open &&
    m2.low > m4.high + c.gapPrice &&
    (m3.close - m3.open) > c.spikeMultiplier * (m2.close - m2.open) &&
    (m3.close - m3.open) > c.spikeMultiplier * (m3.close - m4.close - (m3.open - m4.open))
  );
}

function bearishSetup(data: readonly Candle[], i: number, c: AuthorReplicaConfig): boolean {
  if (i < 4) return false;
  const m4 = data[i - 4]!;
  const m3 = data[i - 3]!;
  const m2 = data[i - 2]!;
  const m1 = data[i]!;
  return (
    m1.high > m2.high &&
    m2.close < m3.close &&
    m2.open < m3.open &&
    m3.close < m4.close &&
    m3.open < m4.open &&
    m2.close < m2.open &&
    m3.close < m3.open &&
    m4.close < m4.open &&
    m2.high < m4.low - c.gapPrice &&
    (m3.open - m3.close) > c.spikeMultiplier * (m2.open - m2.close) &&
    (m3.open - m3.close) > c.spikeMultiplier * (m4.open - m4.close) &&
    (m3.open - m3.close) > c.spikeMultiplier * (m1.open - m1.close)
  );
}

/**
 * Emits the setup/entry represented by the same candle on which the author's
 * trigger condition is observed. This is the research candidate used to
 * compare the implementation against our backtest engine. The live bot adds
 * an explicit pending state; that lifecycle remains separately documented.
 */
export function detectAuthorReplicaCandidates(
  data: readonly Candle[],
  config: AuthorReplicaConfig = DEFAULT_AUTHOR_REPLICA,
): readonly AuthorReplicaSetup[] {
  const out: AuthorReplicaSetup[] = [];
  for (let i = 4; i < data.length; i += 1) {
    const m4 = data[i - 4]!;
    const m2 = data[i - 2]!;
    if (bullishSetup(data, i, config)) {
      const entry = data[i].low;
      const stopLoss = m4.low;
      const risk = entry - stopLoss;
      if (risk > 0 && risk <= config.maxSlDistance) {
        out.push({ direction: 'BUY', setupIndex: i, entryIndex: i, entry, stopLoss, tp1: entry + config.tpR * risk, risk, pGapDistance: m2.low - m4.high });
      }
      continue;
    }
    if (bearishSetup(data, i, config)) {
      const entry = data[i].high;
      const stopLoss = m4.high;
      const risk = stopLoss - entry;
      if (risk > 0 && risk <= config.maxSlDistance) {
        out.push({ direction: 'SELL', setupIndex: i, entryIndex: i, entry, stopLoss, tp1: entry - config.tpR * risk, risk, pGapDistance: m4.low - m2.high });
      }
    }
  }
  return out;
}
