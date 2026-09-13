export type DevSplit = 'DEV' | 'VAL' | 'HOLDOUT';

export interface RawCandle {
  symbol: string;
  timestamp: string;
  timezone: string;
  timeframe: string;
  open: number;
  high: number;
  low: number;
  close: number;
  provider: string;
  datasetVersion: string;
}

export interface CostModel {
  spreadPrice: number;
  slippagePrice: number;
  commissionPrice: number;
}

export interface DevConfig {
  devStart: string;
  devEnd: string;
  valStart: string;
  valEnd: string;
  holdoutStart: string;
  holdoutEnd: string;
  costs: CostModel;
}

export interface DatasetManifest {
  symbol: string;
  provider: string;
  timezone: string;
  timeframe: string;
  datasetVersion: string;
  firstTimestamp: string;
  lastTimestamp: string;
  candleCount: number;
}

export function assignSplit(timestamp: string, config: DevConfig): DevSplit | null {
  if (timestamp >= config.devStart && timestamp <= config.devEnd) return 'DEV';
  if (timestamp >= config.valStart && timestamp <= config.valEnd) return 'VAL';
  if (timestamp >= config.holdoutStart && timestamp <= config.holdoutEnd) return 'HOLDOUT';
  return null;
}

export function adjustedRiskDistance(stopDistance: number, costs: CostModel): number {
  return stopDistance + costs.spreadPrice + costs.slippagePrice + costs.commissionPrice;
}

export function adjustedRMultiple(grossPnl: number, riskDistance: number, costs: CostModel): number {
  if (riskDistance <= 0) throw new Error('riskDistance must be positive');
  const netPnl = grossPnl - costs.spreadPrice - costs.slippagePrice - costs.commissionPrice;
  return netPnl / riskDistance;
}

export function buildDatasetManifest(candles: RawCandle[]): DatasetManifest {
  if (candles.length === 0) throw new Error('dataset must not be empty');
  const first = candles[0]!;
  const last = candles[candles.length - 1]!;
  return {
    symbol: first.symbol,
    provider: first.provider,
    timezone: first.timezone,
    timeframe: first.timeframe,
    datasetVersion: first.datasetVersion,
    firstTimestamp: first.timestamp,
    lastTimestamp: last.timestamp,
    candleCount: candles.length
  };
}

/**
 * G386 deliberately does not generate trades.
 * It only supplies reproducible data/split/cost plumbing for future
 * source-confirmed Strategy A geometry.
 */
export function canonicalExecutionAllowed(): false {
  return false;
}
