import type { DevSplit } from './G386DevHarness.js';

export interface ResearchTradeOutcome {
  split: DevSplit;
  direction: 'LONG' | 'SHORT';
  rMultiple: number;
  holdingBars: number;
  maeR?: number;
  mfeR?: number;
}

export interface ResearchMetrics {
  split: DevSplit;
  trades: number;
  wins: number;
  losses: number;
  winRate: number;
  averageR: number;
  medianR: number;
  expectancyR: number;
  profitFactor: number;
  maxConsecutiveLosses: number;
  averageHoldingBars: number;
}

export function summarizeHypothesisOutcomes(
  outcomes: readonly ResearchTradeOutcome[],
  split: DevSplit
): ResearchMetrics {
  const rows = outcomes.filter((o) => o.split === split);
  const rs = rows.map((o) => o.rMultiple).sort((a, b) => a - b);
  const wins = rows.filter((o) => o.rMultiple > 0).length;
  const losses = rows.filter((o) => o.rMultiple < 0).length;
  const grossWin = rows.filter((o) => o.rMultiple > 0).reduce((s, o) => s + o.rMultiple, 0);
  const grossLoss = Math.abs(rows.filter((o) => o.rMultiple < 0).reduce((s, o) => s + o.rMultiple, 0));
  let maxStreak = 0;
  let streak = 0;
  for (const o of rows) {
    if (o.rMultiple < 0) { streak += 1; maxStreak = Math.max(maxStreak, streak); }
    else streak = 0;
  }
  const sum = rs.reduce((s, r) => s + r, 0);
  const medianR = rs.length === 0 ? 0 : rs.length % 2 === 1 ? rs[(rs.length - 1) / 2]! : (rs[rs.length / 2 - 1]! + rs[rs.length / 2]!) / 2;
  return {
    split,
    trades: rows.length,
    wins,
    losses,
    winRate: rows.length === 0 ? 0 : wins / rows.length,
    averageR: rows.length === 0 ? 0 : sum / rows.length,
    medianR,
    expectancyR: rows.length === 0 ? 0 : sum / rows.length,
    profitFactor: grossLoss === 0 ? (grossWin > 0 ? Number.POSITIVE_INFINITY : 0) : grossWin / grossLoss,
    maxConsecutiveLosses: maxStreak,
    averageHoldingBars: rows.length === 0 ? 0 : rows.reduce((s, o) => s + o.holdingBars, 0) / rows.length
  };
}
