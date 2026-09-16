# SP2L Source Reconciliation — F09–F14 — 2026-09-16

## Purpose

Reconcile the recovered primary transcript, the existing visual geometry triangulation, and the deterministic discrimination fixtures. This is a research/audit artifact only. It does not freeze executable geometry.

## Evidence hierarchy

`Primary source meaning > source visuals > fixture discrimination > backtest performance`.

A visual example can narrow a demonstrated variant, but cannot be generalized to all Spike variants unless the source explicitly supports that generalization. A fixture can expose competing interpretations, but cannot select the canonical rule by itself.

## Reconciliation matrix

| ID | Transcript evidence | Visual evidence | Fixture role | Current source resolution | Canonical action |
|---|---|---|---|---|---|
| F09 | 38:38–39:26: correction/Limit sequence; entry is placed during the structure. 39:48–40:07: order may be updated as structure and stop distance change. | 38:40–39:50: demonstrated bullish sequence shows Buy Limit moving upward with the currently relevant completed higher-low while SL remains deeper/base-structural. | F09 must keep `entry != Leg2 start` as a discrimination question and preserve competing anchors. | **PARTIAL** — dynamic/relevant-HL interpretation is strongly supported for the demonstrated bullish variant; universal exact entry anchor remains unresolved. | **UNRESOLVED** |
| F10 | 39:26: return to referenced structural level invalidates the setup; stop and entry are distinct. | Same sequence shows SL below the Buy Limit and near the deeper/base structural low. | F10 must discriminate structural invalidation from risk-derived stop and wick/body variants. | **PARTIAL** — structural invalidation is source-supported; exact OHLC anchor, wick/body semantics, and buffer remain unresolved. | **UNRESOLVED** |
| F11 | 39:48: delete/re-place may occur after a new candle. 40:07: materially changed stop distance leads to new order/new sizing; small change can retain/move existing order. | Visual movement of pending reference is consistent with evolving structure. | F11 must preserve refresh-on-change vs material-change vs retain interpretations. | **PARTIAL / BEHAVIOR CONFIRMED** — refresh behavior is source-confirmed, but no deterministic mandatory threshold is stated. | **UNRESOLVED** |
| F12 | 40:42–41:03 and 53:16: one-, two-, and three-candle structures plus bar/key-bar variants are source-described. | No visual generalization is required to establish the existence of the family. | F12 must prevent a false `three-candle-only` canonical rule and preserve classifier/precedence alternatives. | **PARTIAL** — family confirmed; acceptance algorithm and precedence unresolved. | **UNRESOLVED** |
| F13 | 22:43: 2X associated with approximately half target distance. 38:05 and 41:26–41:53: optional later/second position and larger-R example. 57:14: later example. | Existing source notes require direct visual/value confirmation before selecting the exact half-target reference. | F13 compares candidate half-target anchors without choosing one. | **PARTIAL** — optional 2X and half-target concept confirmed; exact price anchor, sizing, stop and execution semantics unresolved. | **UNRESOLVED** |
| F14 | 36:15 and 36:59–37:08: SPIKE-2LEG linked to AB=CD; Leg 2 expected equal to Leg 1. 1:02:41–1:03:19: later leg hierarchy example. | Visual notes support a magnitude relationship, but do not uniquely label four OHLC/swing endpoints. | F14 compares wick/body/structural-pivot A/B/C/D candidates and exact equality only as a discrimination fixture. | **PARTIAL** — `Leg2Magnitude ≈ Leg1Magnitude` is source-aligned; A/B/C/D anchors and tolerance unresolved. | **UNRESOLVED** |

## P-Gap cross-cutting blocker

31:43, 34:25–35:37, and 50:09 establish P-Gap as a source-distinguished breakout concept and show multiple ordering variants. The transcript does not uniquely specify an OHLC equation. Therefore P-Gap remains **UNRESOLVED** and must not be replaced by a generic imbalance formula.

## What is now safe to carry forward

- Pending Limit is part of the demonstrated entry sequence.
- Entry and structural invalidation are separate concepts.
- The demonstrated bullish sequence supports a dynamic/relevant higher-low entry candidate.
- Pending-order refresh is a source-supported behavior, but its mandatory threshold is not deterministic.
- Triggering is a family, not a source-proven universal three-candle-only rule.
- 2X is an optional later position and is associated with approximately half-target positioning in the source; exact executable math is unresolved.
- SP2L/2Leg is explicitly connected to AB=CD and the source expects the second leg to match the first in magnitude; exact four-point geometry is unresolved.

## Explicitly not frozen

- Universal `Entry = latest swing low`.
- Universal entry = Leg-2 origin.
- Exact stop OHLC point, wick/body rule, or buffer.
- Numeric/mandatory Limit refresh threshold.
- Universal trigger classifier or precedence.
- Exact 2X price formula, sizing, stop, or fill semantics.
- Exact A/B/C/D definitions or AB=CD tolerance.
- Exact P-Gap OHLC formula.
- Any production BUY/SELL logic.

## Gate decision

Source Resolution: **PARTIAL / materially strengthened**.

Synthetic Fixtures: **ADVANCED**.

Frozen Geometry: **BLOCKED**.

Untouched Validation: **LOCKED**.

Robustness/Stability: **LOCKED**.

Fresh Holdout: **LOCKED**.

Production: **OFF**.

## Next evidence acquisition

1. Obtain source visual/value evidence that labels the entry anchor and Leg-2 origin together for F09.
2. Obtain an explicit stop example for F10 that resolves wick/body/OHLC semantics.
3. Obtain a source example that states the mandatory refresh condition for F11.
4. Obtain an executed setup that identifies trigger selection/precedence for F12.
5. Obtain a worked 2X example with exact levels and sizing/stop semantics for F13.
6. Obtain a worked AB=CD example with four observable endpoints and measurement convention for F14.

No evidence gap may be filled by optimization or backtest selection.
