# SP2L Source Feature Registry — 2026-09-20

## Purpose

Document the separation between:

1. **SOURCE_CONFIRMED_CONCEPT** — an author concept confirmed by direct
   primary source evidence (speech, slide text, labeled frames), carrying
   no executable meaning on its own.
2. **RESEARCH_FEATURE** — an implementation-side construction used for
   research/backtesting, explicitly not source-backed unless stated.
3. **EXECUTABLE_GEOMETRY** — a deterministic, machine-readable rule
   (price fields, indices, events, tolerances) uniquely determined by
   primary source evidence. None exists for any feature below.
4. **FROZEN_GEOMETRY** — geometry promoted for validation/production use.
   **Frozen Geometry remains BLOCKED.** Nothing in this registry promotes
   any feature toward it.

Governing principles:

- Source evidence outranks implementation. Proximity is not equivalence;
  co-location in one passage is not a relation; teaching order is not
  precedence.
- Concept status and executable status are tracked separately. A
  SOURCE_CONFIRMED_CONCEPT with unresolved executable geometry stays out
  of Frozen Geometry.
- Unresolved status is preserved explicitly per feature. Silence in the
  source is recorded as absence, not ambiguity to be filled by inference.

Evidence base (audit-only, no new extraction in this document):

- SP2L training video + transcript blob `47f8673` (frame audit
  `SP2L_RAW_VIDEO_FRAME_AUDIT_2026-09-20.md`).
- Author gap video (dependency audit; resolution update
  `SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md`).
- Author Protective Stops Part1/Part2 and Signal Bar / Key Bar videos
  (dependency audits; frame surveys only, audio unaudited).
- Bridge-statement hunt and dependency closure matrix (session findings).

---

## 1. P-Gap Feature

Status: **SOURCE_CONFIRMED_CONCEPT**

Confirmed:

- P-Gap means Pressure Gap (گپ فشار).
- Distinguished from E-Gap.
- Context:
  - pressure phase
  - pause/compression
  - trend-bar appearance
  - continuation expectation

Unresolved:

- OHLC formula
- candle indexing
- endpoints
- wick/body semantics
- bullish/bearish mirror
- executable detector

Implementation:

Existing PGAPResearch.ts or similar logic is IMPLEMENTATION ONLY, not
source-backed.

---

## 2. AB=CD / 2Leg Feature

Status: **SOURCE_CONFIRMED_CONCEPT**

Confirmed:

- Author explicitly links 2Leg and AB=CD.
- Leg1 and Leg2 equality is an expectation.

Unresolved:

- A/B/C/D anchors
- pivot selection
- measurement method
- tolerance
- completion rule

---

## 3. Key Bar Feature

Status: **SOURCE_CONFIRMED_CONCEPT**

Confirmed:

- Key Bar = Follow Through candle in breakout validation.

Unresolved:

- Key Bar = Second Leg trigger
- activation event
- trigger precedence
- 1/2/3 candle selection rule

---

## 4. Protective Stop Feature

Status: **SOURCE_CONFIRMED_CONCEPT**

Confirmed:

- Protective stop behind structural candle concept exists.
- Generic MM material references Signal Bar.

Unresolved:

- Spike-origin candle = Signal Bar
- Signal Bar as SP2L SL owner
- wick/body anchor
- buffer
- invalidation event

---

## 5. 2X Feature

Status: **SOURCE_CONFIRMED_CONCEPT**

Confirmed:

- 2X is optional.
- Money-management layer.
- Half-target relationship exists.

Unresolved:

- target definition
- coordinate anchor
- sizing
- fill semantics
- lifecycle

---

## Feature Promotion Rule

A feature cannot become Frozen Geometry unless:

1. Direct author source exists.
2. Scope matches SP2L.
3. Executable meaning is explicit.
4. No unresolved geometry remains.
5. Validation confirms stability.

No feature in this registry satisfies all five conditions today.
Frozen Geometry remains **BLOCKED**.

---

## Related

- `SP2L_PGAP_SOURCE_RESOLUTION_UPDATE_2026-09-20.md`
- `SP2L_RAW_VIDEO_FRAME_AUDIT_2026-09-20.md`
- `SP2L_SOURCE_RESOLUTION_CLOSURE_REPORT_2026-09-20.md`
- `SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md`
- `SP2L_SOURCE_TO_GAP_TRACEABILITY_MAP_2026-09-20.md`
- `SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`


## Dependency-gate cross-check — 2026-09-21
F08/F09/F10/F14 are cross-linked only where the source reconstruction creates a structural dependency. This does not promote any unresolved anchor, tolerance, or execution semantics. The dependency matrix is a research control against accidental canonicalization.


### F08 latest resolution status
F08 swing selection has expanded hypothesis/counterexample coverage. Source supports structural turning areas, but no deterministic pivot/window or wick/body field has been promoted. Status remains unresolved.


## Coverage audit checkpoint — 2026-09-21
F08–F15 coverage is consolidated. Seven feature families remain source/execution blockers; F13 is only partially source-confirmed. No canonical promotion occurred.
