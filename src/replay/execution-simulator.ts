import type { Candle, SignalCandidate } from "../domain/market.js";
import type { TradeExit, TradeLedger } from "./trade-ledger.js";

export interface PendingOrder {
  readonly id: string;
  readonly candidate: SignalCandidate;
  readonly createdAt: string;
}

export type FillRule = "UNRESOLVED" | "TOUCH_ENTRY";
export type IntrabarRule = "OHLC_AMBIGUOUS";

export interface ExecutionSimulatorConfig {
  /**
   * Fill semantics are intentionally explicit. UNRESOLVED is the safe default
   * for Strategy A until the source freezes the exact pending-limit fill rule.
   * TOUCH_ENTRY is a research hypothesis, not a canonical source rule.
   */
  readonly fillRule: FillRule;
  /** OHLC cannot establish stop-vs-target ordering within one candle. */
  readonly intrabarRule: IntrabarRule;
}

export interface ExecutionEvent {
  readonly type: "PENDING" | "FILLED" | "STOP" | "TARGET" | "CANCELLED" | "AMBIGUOUS";
  readonly tradeId: string;
  readonly timestamp: string;
}

/**
 * Research execution simulator. It never invents source semantics.
 *
 * A pending order created by a signal is not eligible for a fill on the same
 * candle. This prevents same-candle look-ahead when the signal itself was
 * generated from that candle's OHLC.
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
    if (this.config.fillRule === "UNRESOLVED") throw new Error("FILL_RULE_UNRESOLVED");
    const order: PendingOrder = { id, candidate, createdAt: candidate.timestamp };
    this.pending.set(id, order);
    return { type: "PENDING", tradeId: id, timestamp: candidate.timestamp };
  }

  public onCandle(candle: Candle): readonly ExecutionEvent[] {
    const events: ExecutionEvent[] = [];
    const filledThisCandle = new Set<string>();

    for (const [id, order] of this.pending) {
      // Never infer a fill from the same candle that created the order.
      if (candle.timestamp <= order.createdAt) continue;
      if (this.config.fillRule === "TOUCH_ENTRY" && this.touches(candle, order.candidate.entryPrice)) {
        this.pending.delete(id);
        this.ledger.open(order.candidate, id);
        this.active.add(id);
        filledThisCandle.add(id);
        events.push({ type: "FILLED", tradeId: id, timestamp: candle.timestamp });
      }
    }

    for (const id of [...this.active]) {
      // A candle that establishes the fill must not also establish the exit.
      // OHLC does not reveal the intrabar order of entry versus SL/TP.
      if (filledThisCandle.has(id)) continue;

      const trade = this.ledger.all().find((item) => item.id === id);
      if (!trade) throw new Error(`LEDGER_TRADE_MISSING:${id}`);
      const stop = this.touches(candle, trade.stopPrice);
      const target = this.touches(candle, trade.targetPrice);
      if (stop && target) {
        // OHLC alone cannot determine which was hit first. Do not fabricate it.
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
