import type {
  Candle,
  EngineDecision,
  MarketSnapshot,
  SignalCandidate,
  StrategyProvenance,
} from "../domain/market.js";

export interface StrategyDetector {
  readonly id: string;
  readonly provenance: StrategyProvenance;
  evaluate(history: readonly MarketSnapshot[]): EngineDecision;
}

export interface EngineConfig {
  readonly symbol: string;
  readonly timeframe: string;
  readonly strategy: StrategyDetector;
}

/**
 * Execution-neutral replay engine.
 *
 * This class deliberately does not encode unresolved Strategy A geometry.
 * A detector may only emit a signal when its provenance is canonical=true.
 * Non-canonical hypotheses are observable in research but cannot cross this
 * production-facing boundary.
 */
export class DeterministicEngine {
  private readonly history: MarketSnapshot[] = [];

  public constructor(private readonly config: EngineConfig) {}

  public push(candle: Candle): EngineDecision {
    if (candle.timeframe !== this.config.timeframe) {
      return {
        status: "BLOCKED",
        reason: `TIMEFRAME_MISMATCH:${candle.timeframe}`,
      };
    }

    const previous = this.history[this.history.length - 1];
    if (previous && candle.timestamp <= previous.candle.timestamp) {
      return {
        status: "BLOCKED",
        reason: `NON_MONOTONIC_TIMESTAMP:${candle.timestamp}`,
      };
    }

    const snapshot: MarketSnapshot = {
      symbol: this.config.symbol,
      candle,
      index: this.history.length,
    };
    this.history.push(snapshot);

    const decision = this.config.strategy.evaluate(this.history);
    return this.guardCanonicalBoundary(decision, candle);
  }

  public snapshots(): readonly MarketSnapshot[] {
    return this.history;
  }

  private guardCanonicalBoundary(decision: EngineDecision, candle: Candle): EngineDecision {
    if (decision.status !== "SIGNAL") return decision;

    const candidate = decision.candidate;
    if (!candidate) {
      return { status: "BLOCKED", reason: "SIGNAL_WITHOUT_CANDIDATE" };
    }

    if (candidate.symbol !== this.config.symbol) {
      return { status: "BLOCKED", reason: "SIGNAL_SYMBOL_MISMATCH" };
    }

    if (candidate.timestamp !== candle.timestamp) {
      return { status: "BLOCKED", reason: "SIGNAL_TIMESTAMP_MISMATCH" };
    }

    if (!candidate.provenance.canonical) {
      return {
        status: "BLOCKED",
        reason: "NON_CANONICAL_STRATEGY_CANNOT_EMIT_SIGNAL",
      };
    }

    if (candidate.provenance.ruleIds.length === 0) {
      return { status: "BLOCKED", reason: "SIGNAL_WITHOUT_RULE_PROVENANCE" };
    }

    return this.validateCandidate(candidate);
  }

  private validateCandidate(candidate: SignalCandidate): EngineDecision {
    if (candidate.riskPrice <= 0) {
      return { status: "BLOCKED", reason: "NON_POSITIVE_RISK" };
    }

    const expectedR = Math.abs(candidate.targetPrice - candidate.entryPrice) /
      candidate.riskPrice;
    if (!Number.isFinite(expectedR) || Math.abs(expectedR - candidate.expectedR) > 1e-9) {
      return { status: "BLOCKED", reason: "EXPECTED_R_INCONSISTENT" };
    }

    return { status: "SIGNAL", reason: "CANONICAL_SIGNAL", candidate };
  }
}
