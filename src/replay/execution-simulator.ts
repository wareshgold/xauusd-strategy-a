import type { Candle, Direction, SignalCandidate } from "../domain/market.js";
import type { TradeExit, TradeLedger } from "./trade-ledger.js";

export interface PendingOrder {
  readonly id: string;
  readonly candidate: SignalCandidate;
  readonly createdAt: string;
}

export interface ExecutionSimulatorConfig {
  /** Source-confirmed fill semantics must be supplied by the caller. */
  readonly fillRule: "TOUCH_ENTRY";
  /** Source-confirmed same-candle event ordering must be supplied by the caller. */
  readonly intrabarRule: "OHLC_AMBIGUOUS";
}

export interface ExecutionEvent {
  readonly type: "PENDING" | "FILLED" | "STOP" | "TARGET" | "CANCELLED" | "AMBIGUOUS";
  readonly tradeId: string;
  readonly timestamp: string;
}

/**
 * Execution-neutral simulator. It deliberately refuses to resolve an OHLC
 * candle where both stop and target are touched: intrabar ordering is not
 * inferred from OHLC alone.
 */
export class ExecutionSimulator {
  private readonly pending = new Map<string, PendingOrder>();
  private readonly active = new Set<string>();

  public constructor(
    private readonly ledger: TradeLedger,
    private readonly config: ExecutionSimulatorConfig,
  ) {}

  public submit(candidate: SignalCandidate, id: string): ExecutionEvent {
    if (this.pending.has(id) || this.active.has(id)) throw new Error(`DUPLICATE_EXECUTION_ID:${id}`);
    if (this.config.fillRule !== "TOUCH_ENTRY") throw new Error("UNSUPPORTED_FILL_RULE");
    const order: PendingOrder = { id, candidate, createdAt: candidate.timestamp };
    this.pending.set(id, order);
    return { type: "PENDING", tradeId: id, timestamp: candidate.timestamp };
  }

  public onCandle(candle: Candle): readonly ExecutionEvent[] {
    const events: ExecutionEvent[] = [];
    for (const [id, order] of this.pending) {
      if (this.touches(candle, order.candidate.entryPrice)) {
        this.pending.delete(id);
        this.ledger.open(order.candidate, id);
        this.active.add(id);
        events.push({ type: "FILLED", tradeId: id, timestamp: candle.timestamp });
      }
    }

    for (const id of [...this.active]) {
      const trade = this.ledger.all().find((item) => item.id === id);
      if (!trade) throw new Error(`LEDGER_TRADE_MISSING:${id}`);
      const stop = this.touches(candle, trade.stopPrice);
      const target = this.touches(candle, trade.targetPrice);
      if (stop && target) {
        events.push({ type: "AMBIGUOUS", tradeId: id, timestamp: candle.timestamp });
        continue;
      }
      if (stop) {
        this.close(id, { timestamp: candle.timestamp, price: trade.stopPrice, reason: "STOP" });
        events.push({ type: "STOP", tradeId: id, timestamp: candle.timestamp });
      } else if (target) {
        this.close(id, { timestamp: candle.timestamp, price: trade.targetPrice, reason: "TARGET" });
        events.push({ type: "TARGET", tradeId: id, timestamp: candle.timestamp });
      }
    }
    return events;
  }

  public cancel(id: string, timestamp: string): ExecutionEvent {
    if (!this.pending.delete(id)) throw new Error(`UNKNOWN_PENDING_ID:${id}`);
    return { type: "CANCELLED", tradeId: id, timestamp };
  }

  private close(id: string, exit: TradeExit): void {
    this.ledger.close(id, exit);
    this.active.delete(id);
  }

  private touches(candle: Candle, price: number): boolean {
    return candle.low <= price && price <= candle.high;
  }
}
