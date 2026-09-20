# SP2L F10/F11/F12/F14 — Evidence Gap Matrix — 2026-09-20

## Purpose

Consolidated evidence-gap matrix for the four tracked source-resolution
blockers **F10 / F11 / F12 / F14**, grounded in the archived source evidence and
the 2026-09-19 resolution audits.

This document answers, per blocker:
- what the current evidence is;
- what is confirmed vs not confirmed;
- what evidence **can** close it vs **cannot**;
- the exact primary evidence still required to close it.

It is **documentation only**:
- no missing geometry is inferred;
- no formula, threshold, buffer, precedence, sizing, or fill rule is created;
- nothing is promoted to canonical;
- no strategy code is changed.

This matrix supersedes the earlier 2026-09-16 gap register
(`SP2L_SOURCE_RESOLUTION_GAP_REGISTER_F11_F14_PGAP_2026-09-16.md`) and the
2026-09-16 closure plan (`SP2L_EVIDENCE_GAP_CLOSURE_PLAN_V1_2026-09-16.md`) by
incorporating the materially refined confirmed/unresolved findings from the
2026-09-19 audits.

## Source basis

Resolution audits (all 2026-09-19):
- F10 — `SP2L_F10_INVALIDATION_SL_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`
- F11 — `SP2L_F11_PENDING_ORDER_LIFECYCLE_RESOLUTION_AUDIT_2026-09-19.md`
- F12 — `SP2L_F12_TRIGGER_ACCEPTANCE_PRECEDENCE_RESOLUTION_AUDIT_2026-09-19.md`
- F14 — `SP2L_F14_ABCD_ANCHOR_RESOLUTION_AUDIT_2026-09-19.md`

Supporting status/pack docs:
- `SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md`
- `SP2L_SOURCE_DISCRIMINATION_PACK_F10_F11_F12_F14_2026-09-19.md`
- `SP2L_F10_F11_F12_F14_SOURCE_PASS_INDEX_2026-09-19.md`
- `SP2L_SOURCE_DISCRIMINATION_BATCH_CHECKPOINT_2026-09-19.md`
- `SP2L_SOURCE_DISCRIMINATION_REVIEW_MATRIX_2026-09-20.md`

STATUS vocabulary (as used by the audits):
**SOURCE-CONFIRMED · SOURCE-SUPPORTED · PARTIAL / UNRESOLVED · UNRESOLVED**.

---

## Evidence gap matrix

### F10 — Invalidation / Stop-Loss anchor

| Dimension | State |
|---|---|
| Current evidence | Primary transcript + Batch34/35 visuals: SL placed behind the candle from which the spike originated; separate `Buy Limit` vs `SL` reference levels; return toward/to the referenced level invalidates the scenario. |
| Current status | **PARTIAL / UNRESOLVED** |
| Confirmed | SL structurally tied to spike-origin candle (SOURCE-CONFIRMED). Entry and SL are separate levels (SOURCE-CONFIRMED). Return through relevant structure relates to invalidation (SOURCE-SUPPORTED). |
| Not confirmed | Exact bullish SL price field; exact bearish SL price field; wick vs body; buffer/offset; touch vs penetration vs close; broker bid/ask, spread/slippage semantics. |
| Evidence that CAN close | A labelled source price field showing the SL level at price resolution, plus the invalidation event (touch / wick / close). |
| Evidence that CANNOT close | Backtest-derived SL offsets; a generic "SL below structure" convention; any fixed 50–80 pip rule; inferred wick/body choice. |
| Exact primary evidence required | **One or more labelled source frames / worked examples exposing the exact OHLC field behind the spike-origin candle for both directions, and the observable invalidation event — with no reliance on performance.** |

IP note: the source does establish the *concept* "SL is associated with /
placed behind the spike-origin candle," but no archived evidence uniquely
selects the price field or the executable event.

---

### F11 — Pending-order lifecycle / delete-refresh

| Dimension | State |
|---|---|
| Current evidence | Transcript (~39:48): when a subsequent candle forms, the existing order may be deleted and a new order placed to the changed distance to the stop. Batch34 records an explicit `delete` annotation. |
| Current status | **PARTIAL / UNRESOLVED** |
| Confirmed | Pending Buy Limit can exist before activation (SOURCE-CONFIRMED). Existing order can be deleted (SOURCE-CONFIRMED). A replacement / new order can follow (SOURCE-CONFIRMED). |
| Not confirmed | Mandatory deletion predicate (what observable event forces delete/re-place); numeric candle or time expiry; exact replacement condition; replacement-price construction; candidate precedence; fill/activation semantics. |
| Evidence that CAN close | A source statement/frames uniquely defining the deletion predicate (candle-count / time / new-candidate / stop-distance), the replacement-price rule, and precedence among multiple candidates. |
| Evidence that CANNOT close | The previously discussed "1–2 candle" assumption; automatic modification vs cancel/re-place preference; "newest-candidate-wins" precedence; fixed time expiry; performance-based selection. |
| Exact primary evidence required | **A primary statement or unambiguous frames defining when deletion/re-placement is mandatory, how the replacement price is constructed, and how competing candidates resolve — with no invented numeric timeout.** |

IP note: the source demonstrates delete/replace exists but does not make it
mandatory or deterministic across examples.

---

### F12 — Trigger acceptance / precedence

| Dimension | State |
|---|---|
| Current evidence | Directional trigger concept: bullish corrective candle reaches the low of the previous candle; bearish reaches the high of the previous candle; entry taken after the Second Leg triggers, in spike direction. Source also describes 1/2/3-candle structures and Bar/Key-Bar confirmation variants. |
| Current status | **PARTIAL / UNRESOLVED** |
| Confirmed | Second-Leg trigger is part of SP2L (SOURCE-CONFIRMED). Bullish prev-candle-low reference (SOURCE-CONFIRMED). Bearish prev-candle-high reference (SOURCE-CONFIRMED). Entry follows trigger in spike direction (SOURCE-CONFIRMED). 1/2/3-candle and Bar/Key-Bar variants source-described (SOURCE-CONFIRMED). |
| Not confirmed | Exact candle-index classifier; exact activation event (touch / wick / close); variant precedence (3>2>1? Key-Bar>Bar?); universal Limit-vs-later-confirmation choice; broker fill semantics. |
| Evidence that CAN close | A worked setup or explicit teaching statement that uniquely maps observable structure to the accepted trigger and resolves precedence when multiple variants are present. |
| Evidence that CANNOT close | Frequency of a variant in examples as proof of precedence; a guessed candle index; assumed candle-close/wick-touch confirmation; a guessed P-Gap formula as prerequisite. |
| Exact primary evidence required | **A source statement/frames uniquely defining the trigger index (which candle), the activation event, and a precedence/selection rule among the described variants.** |

IP note: P-Gap validity is a stated prerequisite for the trigger chain, so F12
cannot fully resolve until the P-Gap OHLC construction is resolved.

---

### F14 — AB=CD anchors

| Dimension | State |
|---|---|
| Current evidence | Primary transcript names SPIKE-2LEG and links the two-leg concept to AB=CD; "second leg expected to equal the first." Batch34 records direct visual evidence of `AB=CD` with multiple local structural points but no A/B/C/D labels. |
| Current status | **PARTIAL / UNRESOLVED** |
| Confirmed | AB=CD is explicitly part of SP2L (SOURCE-CONFIRMED). Leg-2 ≈ Leg-1 magnitude relationship (SOURCE-CONFIRMED). |
| Not confirmed | All four A/B/C/D endpoint identities; endpoint price field (wick/body/OHLC); whether D is observed or projected; local swing/pivot definition; how competing structural points resolve; equality tolerance. |
| Evidence that CAN close | Explicit labels or unambiguous source visual endpoints, plus a measurement convention and (if specified) an equality tolerance. |
| Evidence that CANNOT close | Conventional harmonic-trading A/B/C/D definitions; arbitrary pivot detection; `fill=C`; substituting a level for an endpoint; a percentage/pip/point tolerance; a performance-selected tolerance. |
| Exact primary evidence required | **A labelled or unambiguous worked AB=CD example exposing A/B/C/D endpoints, the measurement convention (which price fields), the observed-vs-projected D status, and any explicit equality tolerance.** |

IP note: the source confirms the *relationship* but provides no machine-readable
endpoint mapping in the currently archived evidence.

---

## Cross-cutting dependency — P-Gap

P-Gap remains the highest-severity unresolved geometry item overall, and a
stated prerequisite for a valid/breakout-qualified setup and the F12 trigger
chain. Its exact OHLC construction is **UNRESOLVED**. No F-level blocker may be
promoted to canonical executable geometry while P-Gap's formula/candle-boundary
semantics stay open.

## Gate consequence

- Source Resolution: **PARTIAL**
- Frozen Geometry: **BLOCKED**
- Validation: PARTIAL (scope blocked)
- Robustness: PARTIAL (descriptive only)
- Fresh Holdout: **BLOCKED** (boundary `2026-09-19 00:00Z` untouched)
- Production / Live: **BLOCKED / DISABLED**

`SOURCE_CONFIRMED executable fields = 0 / 7` (unchanged).

A blocker closes only when direct source evidence uniquely determines the
executable meaning. The "exact primary evidence required" column is the exact
acceptance bar; the "cannot close" column is the explicit rejection bar.

## Related

- [Source Discrimination Review Matrix](docs/research/SP2L_SOURCE_DISCRIMINATION_REVIEW_MATRIX_2026-09-20.md)
- [Source Discrimination Status](docs/research/SP2L_SOURCE_DISCRIMINATION_STATUS_2026-09-19.md)
- [Evidence Gap Closure Plan V1](docs/research/SP2L_EVIDENCE_GAP_CLOSURE_PLAN_V1_2026-09-16.md)
- [Source Resolution Gap Register](docs/research/SP2L_SOURCE_RESOLUTION_GAP_REGISTER_F11_F14_PGAP_2026-09-16.md)