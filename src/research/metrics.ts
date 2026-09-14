import type { TradeRecord } from "../replay/trade-ledger.js";

export interface TradeMetrics {
  readonly closedTrades: number;
  readonly wins: number;
  readonly losses: number;
  readonly winRate: number;
  readonly lossRate: number;
  readonly totalR: number;
  readonly averageR: number;
  readonly medianR: number;
  readonly expectancyR: number;
  readonly grossProfitR: number;
  readonly grossLossR: number;
  readonly profitFactor: number;
  readonly maxDrawdownR: number;
  readonly maxConsecutiveLosses: number;
}

/** Descriptive metrics only; no optimization or parameter selection. */
export function calculateTradeMetrics(trades: readonly TradeRecord[]): TradeMetrics {
  const closed = trades.filter((trade) => trade.realizedR !== undefined);
  const returns = closed.map((trade) => trade.realizedR!);
  const wins = returns.filter((value) => value > 0).length;
  const losses = returns.filter((value) => value < 0).length;
  const grossProfitR = returns.filter((value) => value > 0).reduce((sum, value) => sum + value, 0);
  const grossLossR = returns.filter((value) => value < 0).reduce((sum, value) => sum + Math.abs(value), 0);
  const totalR = returns.reduce((sum, value) => sum + value, 0);
  const ordered = [...returns].sort((a, b) => a - b);
  const medianR = ordered.length === 0 ? 0 : ordered.length % 2 === 1
    ? ordered[(ordered.length - 1) / 2]
    : (ordered[ordered.length / 2 - 1] + ordered[ordered.length / 2]) / 2;

  let equity = 0;
  let peak = 0;
  let maxDrawdownR = 0;
  let consecutiveLosses = 0;
  let maxConsecutiveLosses = 0;
  for (const value of returns) {
    equity += value;
    peak = Math.max(peak, equity);
    maxDrawdownR = Math.max(maxDrawdownR, peak - equity);
    consecutiveLosses = value < 0 ? consecutiveLosses + 1 : 0;
    maxConsecutiveLosses = Math.max(maxConsecutiveLosses, consecutiveLosses);
  }

  return {
    closedTrades: closed.length,
    wins,
    losses,
    winRate: closed.length ? wins / closed.length : 0,
    lossRate: closed.length ? losses / closed.length : 0,
    totalR,
    averageR: closed.length ? totalR / closed.length : 0,
    medianR,
    expectancyR: closed.length ? totalR / closed.length : 0,
    grossProfitR,
    grossLossR,
    profitFactor: grossLossR > 0 ? grossProfitR / grossLossR : grossProfitR > 0 ? Number.POSITIVE_INFINITY : 0,
    maxDrawdownR,
    maxConsecutiveLosses,
  };
}
