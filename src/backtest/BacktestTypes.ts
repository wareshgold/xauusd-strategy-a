export interface BacktestTrade {
  readonly entryIndex: number;
  readonly entryTime: string;
  readonly direction: 'BUY' | 'SELL';
  readonly entry: number;
  readonly stopLoss: number;
  readonly tp1: number;
  readonly tp2: number | null;
  readonly riskDistance: number;
  readonly result: 'TP1' | 'TP2' | 'SL' | 'OPEN' | 'AMBIGUOUS';
  readonly rMultiple: number | null;
}

export interface BacktestMetrics {
  readonly trades: number;
  readonly wins: number;
  readonly losses: number;
  readonly winRate: number;
  readonly averageR: number;
  readonly expectancyR: number;
  readonly profitFactor: number | null;
  readonly maxDrawdownR: number;
  readonly consecutiveLosses: number;
}

export interface BacktestResult {
  readonly trades: readonly BacktestTrade[];
  readonly metrics: BacktestMetrics;
}
