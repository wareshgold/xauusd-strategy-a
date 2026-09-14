export type Direction = "LONG" | "SHORT";

export interface Candle {
  readonly timestamp: string;
  readonly open: number;
  readonly high: number;
  readonly low: number;
  readonly close: number;
  readonly timeframe: string;
}

export interface MarketSnapshot {
  readonly symbol: string;
  readonly candle: Candle;
  readonly index: number;
}

export interface StrategyProvenance {
  readonly strategyId: string;
  readonly version: string;
  readonly ruleIds: readonly string[];
  readonly canonical: boolean;
}

export interface SignalCandidate {
  readonly symbol: string;
  readonly direction: Direction;
  readonly timestamp: string;
  readonly entryType: "PENDING_LIMIT";
  readonly entryPrice: number;
  readonly stopPrice: number;
  readonly targetPrice: number;
  readonly riskPrice: number;
  readonly expectedR: number;
  readonly provenance: StrategyProvenance;
}

export interface EngineDecision {
  readonly status: "NO_SIGNAL" | "SIGNAL" | "BLOCKED";
  readonly reason: string;
  readonly candidate?: SignalCandidate;
}
