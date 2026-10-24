# SP2L Source Resolution Closure Report — 2026-09-20

## Purpose

Single consolidated report on the state of SP2L Source Resolution: what the
archived source evidence resolves, what remains blocked, and what exact primary
evidence would be required to close each remaining blocker.

This report:
- does **not** attempt to close blockers;
- does **not** infer missing geometry;
- does **not** convert implementation evidence or secondary wording into rules.

## 1. What is source-confirmed today

The following structural/conceptual statements are source-confirmed from the
archived primary evidence. They establish **concepts and relationships**, not
executable rules. `SOURCE_CONFIRMED executable fields = 0 / 7` — unchanged.

| Area | Source-confirmed |
|---|---|
| Strategy identity | SP2L = Spike → 2 Leg (two-leg continuation after a spike). |
| Spike / breakout concept | A spike is a powerful move; valid breakout is associated with **P-Gap**; P-Gap is distinguished from E-Gap/common gap. |
| Correction concept | Price corrects after the spike; the pattern is two legs (Leg 1 → correction → Leg 2). |
| Entry concept | After the Second Leg is triggered, entry is taken in the spike direction. |
| Bullish trigger reference | Corrective candle reaches the low of the previous candle. |
| Bearish trigger reference | Corrective candle reaches the high of the previous candle. |
| Trigger family | 1/2/3-candle constructions and Bar/Key-Bar confirmation variants are source-described. |
| SL concept (F10) | SL is placed behind the candle from which the spike originated; entry and SL are separate levels. |
| Pending-order lifecycle (F11) | A pending Buy Limit can exist; an existing order may be deleted and a new order placed to the changed stop distance. |
| AB=CD (F14) | AB=CD is explicitly part of SP2L; the second leg is expected to be approximately/effectively equal in magnitude to the first leg (Leg2 ≈ Leg1). |
| 2X (F13) | Optional later position; half-target example and R comparison confirmed; the 50% secondary-entry relation is source-confirmed. |
| Invalidation | Return through the relevant structure relates to invalidation of the scenario. |

None of the above is a numerically executable geometry rule (no threshold,
index, buffer, price field, tolerance, precedence, or fill semantics).

## 2. What remains blocked

Every executable-geometry blocker remains unresolved. Status detail:

| Blocker | Status | Blocking item |
|---|---|---|
| P-Gap concept | **SOURCE_CONFIRMED_CONCEPT** (sync 2026-09-20) | Concept resolved: P-GAP = «فشار» (pressure) in the author's 4-type gap taxonomy (breakout, pressure, exhaustion, common); contextual definition (10–30 candles pressure → pause → trend-bar → continuation likely); E-GAP = «خستگی» with opposite (reversal) expectation. See `SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md`. Historical note: concept previously tracked inside the single UNRESOLVED row below; no historical finding is removed. |
| P-Gap executable geometry | **UNRESOLVED** | Exact current-SP2L OHLC construction / indexing / mirror / threshold / boundary vs E-Gap. Highest-severity item. |
| F08 — relevant/important swing | PARTIAL / UNRESOLVED | Swing-selection algorithm. |
| F10 — invalidation / SL anchor | PARTIAL / UNRESOLVED | Exact SL price field (wick/body/close/open) and invalidation event. |
| F11 — pending-order lifecycle | PARTIAL / UNRESOLVED | Mandatory delete predicate, timeout, replacement-price rule, precedence. |
| F12 — trigger acceptance / precedence | PARTIAL / UNRESOLVED | Candle index, activation event, variant precedence. |
| F13 — 2X | PARTIAL / UNRESOLVED | Universal formula, sizing, and 2X lifecycle. |
| F14 — AB=CD anchors | PARTIAL / UNRESOLVED | A/B/C/D endpoints, measurement convention, tolerance. |
| F15 — bearish source geometry | PARTIAL / UNRESOLVED | Bearish mirror is not promoted as source evidence. |

Non-canonical (must remain so):
- **Implementation evidence** (e.g. Batch38 author code: `BUY SL = low[-4]`,
  `SELL high[-4]`, `low[-1]<low[-2]` trigger) — cross-confirms concept direction
  only; the batch's own verdicts require source confirmation before freeze.
- **Secondary wording** (e.g. Batch12 TradingFinder "usually the lowest/highest
  point") — non-deterministic, secondary.
- **Legacy author-attributed P-Gap candidate** (bullish "high two bars before vs
  current low") — a candidate hypothesis, not a canonical specification.

## 3. Exact evidence required for future closure

A blocker closes only when **direct primary source evidence uniquely determines
the executable meaning**. Backtest performance, robustness, conventional
definitions, and implementation convenience are insufficient.

| Blocker | Exact primary evidence required |
|---|---|
| F10 / F11 / F12 / F14 | See the [F10/F11/F12/F14 evidence gap matrix](docs/research/SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md): a labelled source frame / worked numerical example / direct author wording that uniquely fixes the price field + event (F10), the deletion predicate + replacement rule (F11), the trigger index + precedence (F12), and the A/B/C/D endpoints + tolerance (F14). |
| P-Gap | An explicit worked calculation, an unambiguous labelled source frame, or an author-hosted transcript/document specifying the current-SP2L formula and boundary. Generic gap terminology is no longer a substitute. |
| F08 / F13 / F15 | Primary evidence identifying the swing-selection algorithm (F08), the complete 2X formula and lifecycle (F13), and the bearish source geometry if it exists (F15). |

The exact close-/cannot-close bars per F10/F11/F12/F14 are recorded in the
evidence gap matrix and the [source-to-gap traceability map](docs/research/SP2L_SOURCE_TO_GAP_TRACEABILITY_MAP_2026-09-20.md).

## 4. Gate status: PASS or PARTIAL?

**Source Resolution remains PARTIAL — it cannot PASS today.**

Why not PASS:
- `SOURCE_CONFIRMED executable fields = 0 / 7` (F08/F10–F16/P-Gap unresolved).
- A full re-audit (2026-09-20) found **no new unique primary-source evidence**;
  all four tracked blockers (F10/F11/F12/F14) remain PARTIAL / UNRESOLVED, and
  P-Gap executable geometry remains UNRESOLVED.
- Sync note (2026-09-20, same date, after the re-audit): the author gap-video
  dependency audit added new primary *concept-level* evidence for P-Gap
  (taxonomy + pressure-gap contextual definition; see
  `SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md`). This moves the P-Gap
  *concept* to SOURCE_CONFIRMED_CONCEPT but contributes zero executable
  geometry, so the gate verdict is unchanged.
- The gate passes only when direct primary evidence uniquely determines the
  executable meaning of every field above.

Why not a blocker-close attempt: closing requires new discriminating primary
source material, not further repository-side analysis. No such material is in
the archive.

## Gate rollup (unchanged)

| Gate | Status |
|---|---|
| Source Resolution | **PARTIAL** |
| Frozen Geometry | **BLOCKED** |
| Validation | PARTIAL (scope blocked) |
| Robustness / Stability | PARTIAL (descriptive only) |
| Fresh Holdout | BLOCKED (boundary `2026-09-19 00:00Z` untouched) |
| Production / Live | BLOCKED / DISABLED |

## Related

- [P-Gap Source Resolution Update (2026-09-20)](docs/research/SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md)
- [F10/F11/F12/F14 Evidence Gap Matrix](docs/research/SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md)
- [Source-to-Gap Traceability Map](docs/research/SP2L_SOURCE_TO_GAP_TRACEABILITY_MAP_2026-09-20.md)
- [Source Discrimination Review Matrix](docs/research/SP2L_SOURCE_DISCRIMINATION_REVIEW_MATRIX_2026-09-20.md)
- [P-Gap Final Source Boundary Audit](docs/research/SP2L_PGAP_FINAL_SOURCE_BOUNDARY_AUDIT_2026-09-19.md)
- [Gate Status Dashboard](docs/research/SP2L_RESEARCH_GATE_STATUS_2026-09-20.md)