# SP2L Source Resolution Blocker Matrix V3 — 2026-09-09

## Current gate state

| Gate | State |
|---|---|
| SOURCE RESOLUTION | PARTIAL PASS — narrowed |
| SYNTHETIC DISCRIMINATION | PASS / ongoing |
| FROZEN GEOMETRY | BLOCKED |
| DEV | LOCKED |
| UNTOUCHED VALIDATION | LOCKED |
| ROBUSTNESS / STABILITY | LOCKED |
| FRESH HOLDOUT | LOCKED |
| PRODUCTION | LOCKED |

## Blockers

| ID | Item | Current source decision | Remaining blocker |
|---|---|---|---|
| B1 | P-Gap | First-class source concept; two event-order constructions accepted | Exact OHLC boundaries remain unresolved |
| B2 | Entry | Pending Limit; relevant structural Low/High is the safe abstraction | Universal exact anchor and wick/body edge unresolved |
| B3 | SL | Structural invalidation distinct from Entry | Exact OHLC anchor, wick/body and buffer unresolved |
| B4 | Trigger | 1/2/3-candle family + key-bar examples | Acceptance/timing taxonomy unresolved |
| B5 | AB=CD | Leg-2 magnitude tied to Leg-1 magnitude | A/B/C/D anchors and tolerance unresolved |
| B6 | Leg2/TP | Separate continuation objective; TP1 preferred in source | Executable projection / TP formula unresolved |
| B7 | Pending update | Replacement permitted when structural/risk distance changes materially | Deterministic threshold/timing unresolved |
| B8 | Bearish mirror | Directional structural mirror strongly supported | Exact bearish OHLC geometry not fully source-proven |

## New source-resolution boundary

The remaining uncertainty is no longer whether SP2L contains the concepts above. The source evidence is strong on those semantics. The unresolved question is the exact executable geometry needed to turn those semantics into a deterministic engine without inventing rules.

## Explicit prohibitions

Do not:

- substitute generic FVG/three-candle imbalance for P-Gap;
- replace pending Limit with market-close reclaim;
- derive SL from risk percentage, ATR or fixed distance;
- choose wick/body from backtest performance;
- choose Entry anchor from profitability;
- invent a pending replacement percentage/point threshold;
- assume Entry equals Leg2 start;
- assume a Fibonacci retracement formula for AB=CD;
- invent an AB=CD tolerance;
- infer universal bearish candle anchors from a single visual example.

## Recommended final source pass

1. P-Gap: isolate the cleanest source constructions and record candle-to-candle range relationships.
2. Entry/SL: compare multiple bullish and bearish examples and determine whether a unique structural anchor is explicitly reused.
3. Pending update: distinguish source-confirmed structural movement from discretionary money-management commentary.
4. Trigger: enumerate the exact visible trigger examples and separate trigger formation from order execution.
5. Leg2/TP: map the narrated Leg1/Leg2 examples without assuming C=Entry or any numeric tolerance.

If the final pass still leaves multiple source-consistent geometries, the correct freeze is a **semantic freeze with explicit unresolved geometry**, not a guessed production formula.
