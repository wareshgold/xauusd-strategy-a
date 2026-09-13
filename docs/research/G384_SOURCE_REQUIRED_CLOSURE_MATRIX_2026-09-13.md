# G384 — Source-Required Closure Matrix

Date: 2026-09-13  
Gate: SOURCE RESOLUTION / FROZEN GEOMETRY
Status: **CLOSURE DECISION — NO NEW SOURCE EVIDENCE**

## Purpose

G383 identified seven dimensions where a deterministic implementation requires authoritative source resolution. G384 closes the current source-search loop by mapping each dimension to the exact evidence needed and recording the present decision. It does **not** invent geometry and does **not** promote any hypothesis to canonical Strategy A.

## Closure matrix

| Dimension | Exact evidence required | Current authoritative evidence | Decision |
|---|---|---|---|
| Trigger timing | Source must identify the candle/state that authorizes the setup/entry transition | Official SP2L material confirms breakout/follow-through, correction and pending-limit mechanism, but does not define a universal machine-state trigger boundary | SOURCE-REQUIRED |
| Pending persistence | Source must state when an unfilled pending order remains valid, is moved, or is cancelled | Video narration explicitly describes moving/deleting the order when later candles form; no complete deterministic persistence rule | SOURCE-REQUIRED |
| Fill timing/semantics | Source must define whether fill is intrabar touch, close, next-open, or another rule | Pending-limit mechanism is confirmed; exact fill semantics are not | SOURCE-REQUIRED |
| Invalidation before fill | Source must define whether/when a pending setup is cancelled before activation and the exact invalidation boundary | Structural invalidation is source-supported; complete pre-fill state transition is not | SOURCE-REQUIRED |
| C timing | Source must define when C exists and whether it is a geometric anchor, event, or post-fill state | AB=CD is explicit, but A/B/C/D anchors and C timing are unresolved | SOURCE-REQUIRED |
| Target mapping | Source must map the AB=CD/Leg-2 relationship and TP1/TP2 concepts to one deterministic canonical exit | Default TP 1:1 and TP1/TP2 examples exist; canonical mapping to executable target remains unresolved | SOURCE-REQUIRED |
| Entry/C coupling | Source must explicitly connect pending-limit price, C, and the correction structure if they are the same/different objects | Entry during correction is confirmed; exact price and C coupling are not | SOURCE-REQUIRED |

## Authoritative-source closure

The current primary corpus has been audited: the official SP2L page, official SP2L video/transcript, source chart frames, official course index, and the dedicated gap lesson. No newly located authoritative artifact resolves the seven dimensions above.

Therefore G384 does **not** continue searching indefinitely and does not convert third-party formulas, pixel measurements, or profitable candidate formulas into Strategy A rules.

## Canonical status

All seven dimensions remain `canonical=false`.

The following remain explicitly prohibited:

- generic gap geometry promoted to P-Gap geometry;
- third-party indicator formulas used as authoritative Strategy A rules;
- pixel-inferred OHLC anchors or offsets;
- invented A/B/C/D points;
- fill price assumed equal to C;
- invented SL offsets;
- fixed 2R/3R target rules;
- generalized candle/session filters not source-confirmed.

## Gate decision

**SOURCE RESOLUTION: COMPLETE FOR CURRENT PRIMARY CORPUS**  
**FROZEN GEOMETRY: BLOCKED**

This is a closure point, not another open-ended research loop. The next permitted work is to freeze the source-confirmed semantic core and design a clearly labelled non-canonical research specification for any experiment that is explicitly intended to test unresolved interpretations. Canonical DEV/VAL remains prohibited until the executable geometry is source-confirmed.
