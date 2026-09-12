# G340 — Source-Resolution Boundary Audit

Date: 2026-09-12  
Parent gate: G339  
Source asset: preserved full SP2L lesson + source transcript  
Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Purpose

Establish whether the source material currently available contains enough explicit evidence to freeze the remaining executable AB=CD anchor geometry, rather than continuing to reinterpret the same visual examples indefinitely.

This is a source-resolution gate only. No historical data, optimization, performance criterion, or holdout was used.

## Audited evidence boundary

The relevant source examples already preserved by G329–G338 were rechecked as one evidence chain:

- `36:59–37:08`: explicit `AB=CD` and `Valid BO = P-Gap` slide;
- `38:38–39:48`: pending-limit correction entry and structural invalidation;
- `41:26–42:37`: TP1/TP2 and R terminology, including 2X/3X reward-selection language;
- `43:27–44:29`: 250/500/1000 described as selectable round/trend-level spacing, not a deterministic TP-distance bridge;
- `01:02:41–01:04:32`: worked example containing deep-leg origin, parent/nested leg hierarchy, correction, lower-high sequence, pending-limit movement, activation, and later parent Leg-1 measurement / target discussion.

## What the source does establish

The combined evidence is sufficient to retain these semantic invariants:

1. A directional spike/breakout can form the first leg structure.
2. A deeper leg origin can be identified separately from the eventual pending entry.
3. A larger parent leg and nested 2-leg structures can coexist.
4. A correction follows the first leg and precedes the continuation.
5. The entry is handled as a pending limit during the correction.
6. Actual fill is not automatically the geometric C anchor.
7. Leg 2 is intended to continue from the correction structure.
8. `AB=CD` is explicitly shown/taught.
9. Leg 2 is described as approximately matching Leg 1 in magnitude.
10. R1/R2 are target/reward outcomes, while the exact executable TP construction remains unspecified.

## What the source does NOT establish

After G337–G339, no source statement or unambiguous chart label has been found that deterministically specifies:

- exact A candle index;
- exact B candle index;
- exact A price field (`high`, `low`, `open`, `close`, or other);
- exact B price field;
- exact C structural event and price field;
- a universal wick/body convention;
- a universal swing/fractal algorithm;
- a universal lower-high count threshold;
- an executable D formula in candle/OHLC terms;
- an AB=CD equality tolerance;
- whether TP1 is exactly D, a partial projection, or another source-defined level;
- whether TP2 is exactly D, an extension, or another source-defined level;
- a deterministic P-Gap formula.

The visual examples constrain implementations but do not supply the missing formal mapping.

## Important negative finding

The source's visible drawing behavior cannot be safely converted into a rule merely by pixel matching. In particular, the audited parent-leg measurement shows endpoint proximity that is not sufficient to establish a single wick-to-wick or body-to-body convention. Likewise, the pending-limit marker and later parent-leg measurement are visibly distinct objects.

Therefore repeated re-measurement of the same frames cannot legitimately produce a canonical OHLC rule without new source evidence.

## Source-resolution stopping rule

G340 establishes a formal boundary:

> If no additional source material introduces an explicit label, verbal definition, or unambiguous chart convention for the unresolved A/B/C/D semantics, those semantics remain unresolved and must be represented as competing research hypotheses.

Backtesting must not be used to decide which unresolved source interpretation is "correct."

## Gate decision

**G340 = PASS — SOURCE RESOLUTION BOUNDARY ESTABLISHED**

This is a positive research result, not a geometry freeze.

```text
SOURCE_RESOLUTION          STRONG PARTIAL / BOUNDARY ESTABLISHED
AB=CD semantic concept     SOURCE-CONFIRMED
Leg2 ≈ Leg1                SOURCE-CONFIRMED
Pending-limit              SOURCE-CONFIRMED
Parent / nested hierarchy  SOURCE-SUPPORTED / STRENGTHENED
A/B exact OHLC             UNRESOLVED
C anchor                   UNRESOLVED
Wick/body                  UNRESOLVED
D formula                  UNRESOLVED
AB=CD tolerance            UNRESOLVED
TP1/TP2 ↔ D                UNRESOLVED
P-Gap formula              UNRESOLVED
FROZEN_GEOMETRY            BLOCKED
DEV                        BLOCKED
VAL                        PROTECTED
FRESH_HOLDOUT              LOCKED
PRODUCTION                 BLOCKED
```

## Next authorized research step

Only two source-first paths are authorized:

1. **New source evidence path:** obtain additional authoritative material that explicitly resolves one or more anchor semantics; or
2. **Competing-model research path:** build a fully parameterized research representation of the unresolved A/B/C/D candidates, using synthetic data only, while keeping every candidate non-canonical.

No historical optimization or live signal implementation is authorized by G340.
