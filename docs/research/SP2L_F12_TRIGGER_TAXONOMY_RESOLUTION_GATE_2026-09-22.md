# SP2L F12 Trigger Taxonomy Resolution Gate — 2026-09-22

## Scope
Resolve the trigger family using primary-source wording/visual evidence and independent author-implementation evidence, without promoting fill semantics or configuration details to canonical rules.

## Source evidence
The primary author-controlled source describes the Second Leg as triggered when the corrective candle reaches the relevant prior candle level: bullish uses the prior candle low; bearish uses the prior candle high. The source therefore establishes a directional prior-candle retest/penetration concept.

Archived visual triangulation also shows a pending Buy Limit model rather than a market close-reclaim model. The correction reaches toward/below the relevant higher-low while the pending order remains the execution mechanism.

## Author implementation cross-confirmation
The inspected author implementation uses the fixed local sequence `-4/-3/-2/-1` and the trigger conditions:
- BUY: `low[-1] < low[-2]`
- SELL: `high[-1] > high[-2]`

This independently reinforces the trigger family: the latest trigger candle breaches the immediately preceding correction candle's directional extreme.

## What is now narrowed
F12 can be represented as a **candidate trigger family**:
`Bullish: trigger-candle low reaches/breaches previous-candle low`
`Bearish: trigger-candle high reaches/breaches previous-candle high`

The author implementation strongly supports the exact indexed form for its implementation version.

## What remains unresolved
- Whether the canonical source means strict breach (`<` / `>`) or equality-inclusive touch (`<=` / `>=`).
- Whether the event is evaluated intrabar on wick/touch or only after candle completion.
- Exact broker-side fill price once the trigger occurs.
- Whether the canonical Strategy A execution uses the same fixed `-4/-3/-2/-1` indexing as the author implementation or only the same semantic relationship.
- Any interaction with pending-order refresh immediately before trigger.

## Explicit non-promotions
- No market-entry-at-close rule.
- No automatic `Fill = C` rule.
- No bid/ask/slippage convention.
- No equality rule inferred from backtest results.
- No numerical tolerance.

## Fixture consequence
The deterministic fixture suite should test at minimum:
1. strict penetration;
2. exact equality/touch;
3. intrabar touch versus completed-candle confirmation;
4. pending-limit already resting versus refreshed immediately before trigger.

These are discrimination fixtures, not parameter optimization.

## Gate status
| Item | Status |
|---|---|
| Directional previous-candle trigger concept | SOURCE-CONFIRMED |
| Author fixed-index trigger candidate | STRONGLY CROSS-CONFIRMED |
| Strict vs equality boundary | UNRESOLVED |
| Intrabar vs close evaluation | UNRESOLVED |
| Fill price semantics | UNRESOLVED |
| Frozen Geometry | BLOCKED |
| Validation / Holdout | LOCKED |
| Production | OFF |

## Decision
F12 is materially narrowed but **not frozen**. The safest canonical statement remains the semantic trigger relationship only: the Second Leg is activated by the correction/trigger reaching the direction-specific prior candle extreme. The exact comparison and execution semantics require source-level discrimination.

No canonical production code was changed.