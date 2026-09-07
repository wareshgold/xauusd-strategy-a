# SP2L G4/G5 Freeze Protocol

**Date:** 2026-09-07
**Branch:** `research/phase29-d-archetype-residual-after-geometry`
**Status:** Research-only — protocol for the next map-track gate; no production Strategy A changes
**Sync point:** `docs/strategy/STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`

## Purpose

Define exactly what happens once the source-fit checker (`checkSourceFit` in `G4G5SourceExtraction.ts`) identifies a G4 endpoint family and a G5 origin candidate from the extracted video frames: how the geometry is frozen **with provenance**, and what fixture, gate, and validation changes follow. This protocol is executable by a future agent without re-deriving decisions.

The Knowledge Map gate this serves:

```text
SOURCE RESOLUTION
  -> deterministic synthetic fixtures          (Phase 38 — done)
  -> frozen candidate geometry                 (THIS PROTOCOL)
  -> chronological DEV
  -> untouched VAL
  -> robustness / stability checks
  -> only then Fresh Holdout
  -> only after validation consider production/live signal integration
```

## 1. Precondition — admissible evidence

Before any freeze decision, the extraction record must satisfy:

1. `validateExtraction(extraction)` returns `valid: true`.
2. At least one segment has readable (non-UNREADABLE) `teacherPointA` + `teacherPointB` (Leg 1 start/end) and a readable `leg2End` (TP1).
3. The decisive G5 segment (Segment 3: `S3-A` deep leg start, `S3-D` pending, `S3-E` activation, `S3-F` TP1) has **at least** `S3-A` and `S3-F` readable; `S3-D`/`S3-E` readable when available.
4. Every point records video time and OHLC element; UNREADABLE points are reported, not guessed.
5. The extraction file is stored with provenance: `docs/strategy/source/G4G5_SOURCE_EVIDENCE_FRAMES.json` (frames) and a per-segment extraction record following the `G4G5SourceExtraction` schema.

## 2. Decision matrix — `checkSourceFit` output

| `g4Identified` / `g5Identified` | Decision |
|---|---|
| unique G4 **and** unique G5, no ambiguity, on ≥1 segment | Proceed to freeze (Step 1). |
| unique on ≥1 segment **and** corroborated by a second segment or the bullish/bearish mirror consistency | Freeze at `SOURCE_CONFIRMED`. |
| unique but not corroborated | Freeze at `CANDIDATE` (usable for fixtures; status upgrade requires corroboration). |
| ambiguity (`g4Ambiguous` / `g5Ambiguous` true) | **No freeze.** Re-extract the ambiguous anchors; if still ambiguous, record `TBD` and keep the discriminating fixtures. Never resolve ambiguity by picking. |
| missing evidence (`MISSING_EVIDENCE` everywhere) | **No freeze.** Re-request the specific frame points; record `TBD`. |
| segments disagree (e.g. Segment 1 says `CORRECTION_EXTREME`, Segment 3 says `OTHER_VISUAL_POINT`) | **No freeze.** Re-extract; disagreement is a red flag, not a vote. |
| `fill`/`pending` identified as C | Impossible by construction (excluded from identification). If a human would conclude otherwise, re-check extraction semantics — fill is an execution event, not a geometric C. |

If the teacher's `S3-A` (deep leg start) price differs from `S3-E` (activation) price, record the difference as explicit source evidence that `fillPrice ≠ C` (identity separation invariant), regardless of the freeze outcome.

## 3. Step 1 — freeze the geometry with provenance

Create a frozen-geometry record (JSON, schemaVersion 1) at `docs/strategy/source/`:

```json
{
  "schemaVersion": 1,
  "frozenGeometry": {
    "leg1EndpointFamily": "STRUCTURAL_POINT_TO_STRUCTURAL_POINT",
    "leg2OriginCandidate": "OTHER_VISUAL_POINT",
    "resolutionStatus": "SOURCE_CONFIRMED",
    "frozenAt": "2026-09-07",
    "sourceBasis": {
      "segments": ["SEGMENT_3"],
      "frames": ["1:04:00", "1:04:19", "1:04:32"]
    },
    "fitEvidence": {
      "segment": "SEGMENT_3",
      "impliedLeg1": 17,
      "impliedTp1": 2519,
      "g4Identified": "STRUCTURAL_POINT_TO_STRUCTURAL_POINT",
      "g5Identified": "OTHER_VISUAL_POINT",
      "fillPriceDiffersFromC": true
    },
    "evidenceRef": "docs/strategy/source/G4G5_SOURCE_EVIDENCE_FRAMES.json",
    "extractionRef": "<per-segment extraction record>"
  }
}
```

Rules:
- The record must cite the exact video times and the extraction record; nothing is memorized or approximated.
- `resolutionStatus` is `SOURCE_CONFIRMED` only when the decision matrix says so; otherwise `CANDIDATE` with a stated reason.
- The frozen record **replaces** the "identify the family" question: from this point the family/candidate is an input, not an output.

Update the synchronization docs:
- `STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md` — gate table: G4 `SEMANTIC RESOLVED / EXECUTABLE FROZEN`, G5 same (or `CANDIDATE` if not corroborated); G6 remains `BLOCKED` until Step 3.
- `SP2L_SOURCE_EVIDENCE_REGISTER_2026-09-07.md` — add the frozen definitions under a new "Frozen geometry" section.
- Write a `RESEARCH_CHECKPOINT_2026-09-07_G4_G5_FROZEN.md` summarizing the evidence and decision.

## 4. Step 2 — replace discriminating fixtures with frozen-geometry fixtures

The Phase 38 discriminating fixtures remain committed as the pre-freeze measurement machinery. In addition:

1. **Positive frozen fixture:** one chart per frozen definition, derived from the actual extracted coordinates (normalized), asserting:
   - `measureLeg1(chart, frozenFamily) === impliedLeg1`;
   - `measureLeg2(chart, frozenCandidate) === impliedLeg1` (exact equality, no tolerance);
   - the frozen family is the **only** matching family under `checkSourceFit`.
2. **Negative frozen fixtures:**
   - C placed at the fill price → rejected as canonical (`EXCLUDED_NON_CANONICAL` must hold);
   - C before correction start → `LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION`;
   - missing teacher anchors → `MISSING_EVIDENCE`, never a guess;
   - a rival family that would fit a *different* implied Leg1 → must not match the frozen definition.
3. **Assertion layer:** add a frozen-mode helper (e.g. `assertFrozenGeometry(chart, frozenFamily, frozenCandidate)`) that throws on any measurement contradicting the frozen definitions. The existing `reportCandidates` stays available for audit, but promotion logic uses only the frozen definitions.
4. Run the sp2l test suite (`pnpm run test:sp2l-g4g5`, plus the full `pnpm test`).

## 5. Step 3 — G6 equality handling

After G4/G5 are frozen:

1. Re-inspect all source examples for an explicit numerical equality criterion. If one exists, freeze it with provenance.
2. If none exists (expected), keep `abs(Leg2) ~= abs(Leg1)` as a source-semantic concept with `EQUALITY_TOLERANCE_TBD`.
3. Any numerical tolerance used later must be a **separately documented simulator/research policy**, never attributed to the teacher, and must not be fitted on historical outcomes.
4. Build positive/negative fixtures around that explicit policy only after this step.

## 6. Step 4 — G7 execution policy validation on fixtures

Using the frozen geometry, validate the Phase 33 G7 policies on fixtures, including:
- pending limit exists before fill; fill at the exact pending price;
- pre-fill structural invalidation cancels the pending order;
- fixed structural stop after fill (never widened);
- TP1 as the base single-position target;
- same-candle entry/SL/TP ordering remains an explicit policy (`SL_FIRST` / `TP_FIRST` / `AMBIGUOUS`) — never resolved optimistically;
- spread/slippage excluded from semantic fixtures.

No G7 policy may be used to repair or redefine the frozen G4/G5 geometry.

## 7. Step 5 — chronological validation (map gate)

Only after Steps 1–4:

1. Implement the frozen SP2L V2 detector/entry in **research-only** code (never in production Strategy A).
2. Run chronological DEV → untouched VAL → robustness/stability checks.
3. No threshold mining, no best-window selection, no VAL/Fresh optimization.
4. Fresh Holdout remains LOCKED until DEV/VAL survival and a separate explicit decision.
5. Only after all gates pass may production/live integration be considered — and never with AI-generated BUY/SELL decisions.

## 8. Hard guardrails (never)

- Never use historical PnL or DEV/VAL results to decide what the source means or to break a freeze ambiguity.
- Never resolve G4/G5 ambiguity by picking the best-performing candidate.
- Never attribute an invented tolerance, buffer, or level to Poorsamadi.
- Never silently convert `fillPrice`, `pendingPrice`, or `correction.low/high` into canonical C.
- Never unlock Fresh Holdout while core geometry is unfrozen.
- Never modify production Strategy A or the canonical baseline semantics.
- Never delete or rewrite Phase 13–30 historical evidence.

## 9. Failure paths

| Situation | Action |
|---|---|
| Frames unrecoverable / blurry | Record `TBD`; re-request only the unreadable points; never estimate. |
| Unique but uncorroborated identification | Freeze at `CANDIDATE`; proceed with fixtures; upgrade on corroboration. |
| Ambiguity or segment disagreement | No freeze; re-extract; if persistent, record `TBD` and stop rather than guess. |
| Evidence contradicts the semantic ordering (Leg2 before correction, etc.) | Treat as extraction error; re-inspect the frame; if confirmed in source, revise the lifecycle doc with provenance. |

## 10. Definition of done

- Frozen-geometry record exists with provenance and a `resolutionStatus`.
- Knowledge map gate table and evidence register updated.
- Positive + negative frozen fixtures pass under the assertion layer.
- G6 tolerance explicitly `TBD` or frozen with provenance; G7 policies validated on fixtures.
- Full test suite green; typecheck clean; all changes research-only and committed on the map-track branch.