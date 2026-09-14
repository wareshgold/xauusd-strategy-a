import type { Direction, SignalCandidate } from "../domain/market.js";

export type TradeStatus = "OPEN" | "WON" | "LOST" | "CANCELLED";

export interface TradeRecord {
  readonly id: string;
  readonly symbol: string;
  readonly direction: Direction;
  readonly signalTimestamp: string;
  readonly entryPrice: number;
  readonly stopPrice: number;
  readonly targetPrice: number;
  readonly riskPrice: number;
  readonly expectedR: number;
  readonly status: TradeStatus;
  readonly exitTimestamp?: string;
  readonly exitPrice?: number;
  readonly realizedR?: number;
}

export type ExitReason = "STOP" | "TARGET" | "CANCELLED";

export interface TradeExit {
  readonly timestamp: string;
  readonly price?: number;
  readonly reason: ExitReason;
}

/**
 * Deterministic trade ledger. It records outcomes; it does not decide whether
 * a Strategy A setup exists. That separation prevents research hypotheses from
 * being smuggled into execution accounting.
 */
export class TradeLedger {
  private readonly trades = new Map<string, TradeRecord>();

  public open(candidate: SignalCandidate, id: string): TradeRecord {
    if (this.trades.has(id)) throw new Error(`DUPLICATE_TRADE_ID:${id}`);
    this.assertFinite("ENTRY_PRICE", candidate.entryPrice);
    this.assertFinite("STOP_PRICE", candidate.stopPrice);
    this.assertFinite("TARGET_PRICE", candidate.targetPrice);
    this.assertFinite("RISK_PRICE", candidate.riskPrice);
    this.assertFinite("EXPECTED_R", candidate.expectedR);
    if (candidate.riskPrice <= 0) throw new Error("NON_POSITIVE_RISK");

    const trade: TradeRecord = {
      id,
      symbol: candidate.symbol,
      direction: candidate.direction,
      signalTimestamp: candidate.timestamp,
      entryPrice: candidate.entryPrice,
      stopPrice: candidate.stopPrice,
      targetPrice: candidate.targetPrice,
      riskPrice: candidate.riskPrice,
      expectedR: candidate.expectedR,
      status: "OPEN",
    };
    this.trades.set(id, trade);
    return trade;
  }

  public close(id: string, exit: TradeExit): TradeRecord {
    const current = this.trades.get(id);
    if (!current) throw new Error(`UNKNOWN_TRADE_ID:${id}`);
    if (current.status !== "OPEN") throw new Error(`TRADE_ALREADY_CLOSED:${id}`);
    if (exit.reason !== "CANCELLED" && exit.price === undefined) {
      throw new Error("EXIT_PRICE_REQUIRED");
    }
    if (exit.price !== undefined) this.assertFinite("EXIT_PRICE", exit.price);

    const realizedR = exit.reason === "CANCELLED"
      ? undefined
      : this.calculateR(current, exit.price!);
    const status: TradeStatus = exit.reason === "CANCELLED"
      ? "CANCELLED"
      : exit.reason === "TARGET"
        ? "WON"
        : "LOST";

    const closed: TradeRecord = {
      ...current,
      status,
      exitTimestamp: exit.timestamp,
      ...(exit.price === undefined ? {} : { exitPrice: exit.price }),
      ...(realizedR === undefined ? {} : { realizedR }),
    };
    this.trades.set(id, closed);
    return closed;
  }

  public all(): readonly TradeRecord[] {
    return [...this.trades.values()];
  }

  public openTrades(): readonly TradeRecord[] {
    return this.all().filter((trade) => trade.status === "OPEN");
  }

  private calculateR(trade: TradeRecord, exitPrice: number): number {
    const signedMove = trade.direction === "LONG"
      ? exitPrice - trade.entryPrice
      : trade.entryPrice - exitPrice;
    return signedMove / trade.riskPrice;
  }

  private assertFinite(field: string, value: number): void {
    if (!Number.isFinite(value)) throw new Error(`NON_FINITE_${field}`);
  }
}
