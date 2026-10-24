# SP2L Source Resolution — Next Parallel Pass — 2026-09-19

## Purpose

Consolidate the current source evidence after the P-Gap closure attempt and the F11/F12/F13/F14/F16 passes, then move the highest-value source work forward in parallel without promoting unresolved geometry.

## Source-aligned chain currently supported

`AB=CD concept`
→ `Valid BO = P-Gap`
→ `correction / Second-Leg structure`
→ `corrective price reaches the referenced previous-candle level`
→ `Second Leg trigger`
→ `entry in spike direction / Buy Limit presentation`
→ `separate structural SL reference`
→ `optional 2X concept`
→ `Round Level concept`

This is a semantic/source chain only. It is not an executable canonical rule set.

## Cross-source results

### P-Gap / C01

Status: **UNRESOLVED / QUARANTINED**

Confirmed:
- P-Gap is distinct from Common/E-Gap in the source.
- Valid breakout/spike is associated with P-Gap.
- Source-described ordering variants are treated as the same strategy concept.

Still missing:
- exact current-SP2L candle indexing;
- bearish mirror;
- exact OHLC/wick/body fields;
- equality/boundary semantics;
- minimum threshold;
- exact qualifying-candle relationship.

Decision: do not reopen generic gap-theory research. Reopen only if a new direct author/source artifact exposes one of the missing fields.

### F12 / Trigger

Status: **PARTIAL / UNRESOLVED**

Confirmed:
- bullish corrective trigger references the previous candle's low;
- bearish corrective trigger references the previous candle's high;
- trigger is followed by entry in spike direction;
- source describes 1/2/3-candle structures and Bar/Key-Bar variants.

Still missing:
- universal candle-index classifier;
- touch/wick/body/close semantics;
- precedence among variants;
- universal choice between predefined Limit placement and later confirmation;
- broker activation/fill semantics.

Decision: the directional trigger relation can be preserved as source evidence, but no single trigger implementation is canonical.

### F10 / SL and invalidation

Status: **PARTIAL / UNRESOLVED**

Confirmed:
- Buy Limit and SL are represented as separate levels;
- structural invalidation is associated with the spike-origin structure.

Still missing:
- exact bullish/bearish OHLC anchor;
- wick/body semantics;
- buffer/offset;
- invalidation event and execution semantics.

Decision: no exact SL formula is promoted.

### F11 / Pending lifecycle

Status: **PARTIAL / UNRESOLVED**

Confirmed:
- pending Buy Limit exists;
- existing order may be deleted;
- a replacement/new order may be placed when the structure/distance changes.

Still missing:
- mandatory delete predicate;
- numeric timeout;
- replacement construction;
- multiple-candidate precedence;
- fill semantics.

Decision: prior 1–2 candle idea remains non-canonical.

### F14 / AB=CD

Status: **PARTIAL / UNRESOLVED**

Confirmed:
- SP2L is explicitly taught as Spike-2Leg;
- AB=CD is explicitly shown/stated;
- Leg2 is expected to be approximately/effectively equal to Leg1.

Still missing:
- exact A/B/C/D endpoints;
- observed versus projected D;
- wick/body/OHLC convention;
- swing selection;
- equality measurement convention;
- tolerance.

Decision: no harmonic/pivot convention, `fill=C`, or arbitrary tolerance is allowed.

### F13 / 2X

Status: **PARTIAL / UNRESOLVED**

Confirmed:
- 2X is a distinct secondary-position concept;
- it is optional in at least one source context;
- author-associated material describes a secondary entry at approximately 50% of the entry-to-SL distance;
- later entry can produce a different/larger R outcome.

Still missing:
- universal mandatory/optional status;
- reference state when initial order is pending/filled/refreshed;
- exact price construction/rounding;
- sizing;
- pending versus immediate lifecycle;
- interaction with refresh and exits.

Decision: no universal 2X equation or size multiplier is promoted.

### F16 / Round Level

Status: **PARTIAL / UNRESOLVED**

Confirmed:
- Round Level is explicitly taught;
- 250, 500, and 1000 point examples are present.

Still missing:
- unit definition;
- rounding function;
- purpose;
- mandatory/optional status;
- symbol/timeframe dependence;
- interaction with entry/target/2X/SL.

Decision: example values remain examples, not a universal parameter.

## Parallel next actions

1. **Primary-source closure attempt only where new evidence can discriminate**
   - F10: search for explicit source wording/visuals tying SL to a named candle/price field.
   - F11: search for explicit lifecycle wording showing why/when the order is deleted/replaced.
   - F12: search for source examples that explicitly distinguish the trigger variants and their activation order.
   - F14: search for a worked AB=CD example that visibly labels A/B/C/D or states how the two legs are measured.
   - F13: search for an explicit 2X worked example with reference price and lifecycle.
   - F16: search for a worked Round Level example with reference price and stated purpose.

2. **Do not spend another generic-theory pass on P-Gap.**
   The current evidence boundary is already documented. New P-Gap work requires direct source evidence, not another conventional-gap hypothesis.

3. **Keep the implementation boundary closed.**
   Synthetic fixtures may test the competing interpretations and fail-closed behavior, but fixtures may not choose the canonical interpretation.

4. **Keep statistical work separated.**
   Existing 4-week robustness/stability evidence remains descriptive research evidence and cannot resolve source ambiguity.

## Gate after this pass

- Source Resolution: **PARTIAL PASS**
- Frozen Geometry: **BLOCKED**
- Historical Validation: **LOCKED**
- Robustness / Parameter Stability: **RESEARCH EVIDENCE ONLY**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Production: **BLOCKED**
- Live Trading: **DISABLED**

## Canonical no-go

Canonical promotion remains allowed only when every required executable geometry field is explicitly `SOURCE_CONFIRMED`. Current source-confirmed executable fields remain **0 / 7**.

## Evidence standard for closing a blocker

A blocker may close only when new evidence uniquely determines the relevant executable meaning, such as:
- an unambiguous labelled primary frame;
- an explicit worked calculation;
- an author-hosted transcript/document with the required rule;
- equivalent direct author evidence.

Backtest performance, conventional trading definitions, symmetry assumptions, or implementation convenience are not admissible substitutes.

## Checkpoint

This document is a research checkpoint for the 2026-09-19 parallel source-resolution pass. It records the boundary before any future source artifact is evaluated.
