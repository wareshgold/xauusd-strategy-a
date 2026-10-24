# SP2L F14 — AB=CD Anchor Resolution Audit — 2026-09-19

## Purpose

Resolve F14 using only source-aligned evidence already archived in the repository. This audit does not infer harmonic-trading conventions, pivot rules, `fill=C`, endpoint substitutions, or numerical tolerance from backtest behavior.

## Evidence reviewed

Primary and previously archived evidence reviewed:

- `docs/research/SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `docs/research/SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `docs/research/SP2L_BATCH35_OFFICIAL_SOURCE_PGAP_2X_RESOLUTION_2026-09-17.md`
- `docs/research/SP2L_F13_F14_SOURCE_DISCRIMINATION_2026-09-16.md`
- `docs/research/SP2L_SOURCE_RESOLUTION_GAP_REGISTER_F11_F14_PGAP_2026-09-16.md`
- `docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`

## Source-confirmed findings

### 1. AB=CD is explicitly part of SP2L

The primary transcript records the strategy name SPIKE-2LEG and explicitly links the two-leg concept to AB=CD. The teaching sequence describes a correction followed by a second leg expected to become equal to the first leg, with the target associated with completion of that second leg.

Batch34 independently records direct visual evidence of `AB=CD` in the primary teaching sequence.

**Status:** magnitude / conceptual relationship = **SOURCE-CONFIRMED**.

### 2. Leg-2 ≈ Leg-1 is source-supported

The source supports the relationship that the second leg is expected to be approximately/effectively equal in magnitude to the first leg.

This does not, by itself, define the four endpoint coordinates required to calculate the relationship deterministically.

**Status:** magnitude relationship = **SOURCE-CONFIRMED**; endpoint geometry = unresolved.

## F14 endpoint test

The source evidence reviewed does **not** uniquely identify all four executable A/B/C/D endpoints.

Specifically, the archived evidence does not provide a deterministic source rule that uniquely answers:

- which exact candle/price is A;
- which exact candle/price is B;
- which exact candle/price is C;
- whether D is an observed endpoint or a projected target;
- whether endpoints use wick extremes, candle bodies, opens/closes, or another price field;
- whether a local swing/pivot definition is required to select the endpoints;
- how competing structural points are resolved when multiple candidates are visible.

Batch34 explicitly records multiple local structural points in the teaching diagram but does not assign deterministic A/B/C/D labels to them.

The transcript confirms the AB=CD relationship but does not supply a machine-readable endpoint mapping.

Therefore there is no source-complete deterministic A/B/C/D mapping in the currently archived evidence.

## Tolerance test

No universal numerical AB=CD tolerance is source-confirmed in the reviewed evidence.

The source does not provide a deterministic statement such as:

- a percentage tolerance;
- a pip/point tolerance;
- a fixed-price tolerance;
- an ATR-relative tolerance;
- a Fibonacci/harmonic tolerance band.

Accordingly, no tolerance may be introduced from conventional harmonic practice, implementation convenience, or backtest performance.

**Status:** tolerance = **UNRESOLVED**.

## Explicitly prohibited in F14

The following remain non-canonical:

- conventional harmonic A/B/C/D definitions;
- arbitrary pivot detection;
- `fill=C`;
- substituting Entry, Buy Limit, or another level for C without source evidence;
- treating the projected D target as an observed candle anchor without source evidence;
- wick/body/OHLC substitution;
- a percentage/pip/point equality tolerance;
- selecting an interpretation because it improves backtest or robustness results.

## Deterministic conclusion

### F14 result: **PARTIAL / UNRESOLVED**

What can be frozen from the source:

`SP2L = Spike → 2 Leg` and the second leg is expected to be approximately/effectively equal to the first leg (AB=CD concept).

What cannot yet be frozen:

`A, B, C, D` endpoint mapping, endpoint price semantics, measurement convention, and tolerance.

This means F14 does **not** close the Frozen Geometry blocker.

## Gate impact

- F14: **PARTIAL / UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- No canonical AB=CD formula promoted.
- No new backtest or robustness tuning justified by this evidence.
- Fresh Holdout remains governed by the existing frozen boundary and eligibility rule.
- `LIVE_TRADING_ENABLE=false` remains unchanged.

## Next source-resolution priority

Because F14 cannot be closed from the currently archived evidence, the next valid research target is the next executable blocker rather than another performance run.

Priority:

1. F11 — deterministic pending-order deletion/refresh lifecycle;
2. F10 — exact invalidation/SL price anchor;
3. F12 — deterministic trigger acceptance/precedence;
4. F13 — complete 2X execution/lifecycle semantics;
5. P-Gap — exact current-SP2L indexing/boundary/mirror semantics.

No unresolved rule should be promoted solely because it produces favorable statistical results.

## Decision

**F14 remains PARTIAL / UNRESOLVED.**

No source evidence currently justifies changing the canonicalization status.
