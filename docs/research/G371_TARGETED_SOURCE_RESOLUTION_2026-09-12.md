# G371 — Targeted Source Resolution

Date: 2026-09-12
Status: SOURCE RESOLUTION / evidence reconciliation
Canonical: false

## Objective

Re-open source resolution only for the geometry blockers identified by G370. No historical performance is used to select an interpretation.

## Authoritative evidence

1. **SP2L source transcript**: `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
2. **SP2L source video**: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4` (local research artifact)
3. **Gap lesson**: `gap پورصمدی دوره جامع.mp4` (local research artifact)
4. **Official SP2L page**: https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

## Findings

### P-Gap
- Source terminology is resolved: P-Gap is the Pressure Gap concept.
- Gap lesson distinguishes Breakout, Pressure, Exhaustion and Common gaps and states that location/context matters.
- The generic bullish gap example uses a candle-index relationship, but that example is not labelled as the executable P-Gap rule.
- SP2L source shows at least two timing variants: breakout → follow-through → P-Gap, and higher-structure/lower-high sequence → P-Gap.
- **Still unresolved:** exact P-Gap endpoints, wick/body basis, overlap rule, minimum size, tolerance and exact candle-sequence predicate.
- Decision: no executable P-Gap formula promoted.

### A/B/C/D and scale
- Source explicitly supports SP2L / 2Leg and AB=CD.
- Source examples distinguish nested/parent moves and identify a deeper leg origin in one example.
- **Still unresolved:** canonical A/B/C/D anchors, whether anchors use wick/body/open/close/candle boundary/structural event, and whether parent or nested scale is canonical.
- Decision: no canonical anchor selector promoted.

### Entry / trigger / fill
- Official page: corrective candle reaches prior low in an uptrend or prior high in a downtrend; entry follows the Spike direction.
- Video source explicitly demonstrates a pending-limit order during correction and distinguishes the order placement/activation sequence.
- **Still unresolved:** exact pending-limit price, whether the source-indicated correction point is itself the limit, and fill semantics when price touches/crosses the level.
- Decision: trigger/fill state distinction is preserved; no formula for fill=C is permitted.

### Stop / invalidation
- Official page: SL is behind the candle from which the Spike originated.
- Video source explicitly describes scenario cancellation at structural invalidation.
- **Still unresolved:** exact side/boundary, wick versus body versus candle boundary, and any offset.
- Decision: structural-origin concept is canonical-semantic only; executable SL geometry remains blocked.

### TP / target mapping
- Official page states default TP = 1:1.
- Video source explicitly contains AB=CD / 2Leg, TP1/TP2 and R1/R2 terminology and examples of 2X/3X outcomes.
- **Still unresolved:** how AB=CD projection maps to TP1/TP2/R1/R2 and how that lesson target hierarchy reconciles with the official default 1:1 statement.
- Decision: no fixed 1R/2R/3R canonical target rule; AB=CD remains source-supported but geometrically unresolved.

### Secondary 50% entry
- Official page explicitly permits a secondary entry at 50% of entry-to-SL distance.
- **Still unresolved:** whether this is part of the canonical Strategy A execution or an optional add-on outside the primary setup.
- Decision: retain as source-supported optionality; do not require it for the canonical primary signal.

## Source-resolution gate result

**BLOCKED — no new authoritative evidence closes the executable geometry blockers.**

The correct next step is not DEV backtesting. The project should either acquire a higher-resolution/annotated primary artifact that explicitly labels the missing geometry, or preserve the current semantic freeze and continue only with non-canonical hypothesis research.

## Promotion guard

The following remain prohibited from canonical Strategy A:
- generic three-candle gap formula as P-Gap;
- guessed A/B/C/D anchors;
- guessed wick/body/close rules;
- `fill_price = C` by convention;
- guessed SL offset;
- fixed 2X/3X TP constants;
- seven lower highs as a universal threshold;
- MA/session/timeframe filters as hard gates unless separately source-confirmed.
