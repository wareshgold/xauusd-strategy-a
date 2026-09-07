# Phase 38 — SP2L G4/G5 Discriminating Synthetic Fixtures

**Date:** 2026-09-07
**Branch:** `research/phase29-d-archetype-residual-after-geometry`
**Status:** Research-only — no production Strategy A changes
**Sync point:** `docs/strategy/STRATEGY_A_POORSAMADI_KNOWLEDGE_MAP_V2_2026-09-07.md`

## Objective

Prove — with deterministic synthetic charts — that the G4 Leg1 endpoint families and the G5 Leg2 origin candidates can be **measured distinctly** on the same chart, so that once the source-visual coordinates arrive (see `G4_G5_VISUAL_FRAME_REQUEST_2026-09-07.md`) the correct family/candidate can be identified instead of guessed.

This is the "deterministic synthetic fixtures" step of the Knowledge Map progression gate. It selects nothing; it makes every alternative measurable and auditable.

## Why "discriminating" fixtures

The G4 families and G5 candidates differ only in which chart point is used. On a normal chart the differences can be invisible. Each fixture below is constructed so that every family/candidate resolves to a **different price anchor**, producing **pairwise-distinct magnitudes** on one chart:

| G4 family | Bull anchors | Bull Leg 1 |
|---|---|---|
| `STRUCTURAL_LOW_HIGH_TO_SPIKE_EXTREME` | firstStructuralLow 2497 → spikeExtreme 2518 | **21** |
| `BREAKOUT_LEVEL_TO_SPIKE_EXTREME` | breakoutLevel 2500 → spikeExtreme 2518 | **18** |
| `SPIKE_START_TO_SPIKE_END` | spikeStart 2504 → spikeExtreme 2518 | **14** |
| `RELEVANT_CANDLE_OPEN_TO_SPIKE_EXTREME` | relevantCandleOpen 2510 → spikeExtreme 2518 | **8** |
| `STRUCTURAL_POINT_TO_STRUCTURAL_POINT` | teacherPointA 2501 → teacherPointB 2518 | **17** |

| G5 candidate | Bull origin | Bull Leg 2 (end 2519) |
|---|---|---|
| `CORRECTION_EXTREME` | 2498 | **21** |
| `STRUCTURAL_HL_LH` | 2501 | **18** |
| `OTHER_VISUAL_POINT` | 2502 | **17** |
| `PENDING_LIMIT` (excluded) | 2500 | **19** |
| `ACTUAL_FILL` (excluded) | 2500 | **19** |

All magnitudes are hand-computed and asserted exactly in the unit tests.

## Fixture catalog

### F1 — Bullish four-anchor discriminator (`BULL_FOUR_ANCHOR_FIXTURE`)

Range (0–4) → breakout close above 2500 (5) → FT (6) → spike (7–8, extreme high 2518) → correction (9–12; pending BUY LIMIT 2500 at index 9, intrabar fill at index 11, correction extreme low 2498, higher low 2501) → Leg 2 (13–14, end high 2519).

```text
idx:   0     1     2     3     4     5     6     7     8     9     10    11    12    13    14
open:  2495  2498  2499  2500  2499  2500  2502  2505  2510  2516  2510  2506  2503  2505  2511
high:  2500  2500  2501  2501  2502  2503  2506  2512  2518  2517  2512  2508  2507  2513  2519
low:   2494  2496  2497  2498  2498  2497  2501  2504  2509  2508  2502  2498  2501  2504  2510
close: 2498  2499  2500  2499  2500  2502  2505  2510  2517  2510  2506  2503  2505  2511  2518
```

Labeled anchors: `breakoutLevel` (2500), `firstStructuralLow` (2497), `spikeStart` (2504), `spikeStartOpen` (2505), `spikeExtreme` (2518), `relevantCandleOpen` (2510), `teacherPointA` (2501), `teacherPointB` (2518), `correctionExtreme` (2498), `structuralHL` (2501), `pendingLimit` (2500), `fill` (2500), `otherVisualPoint` (2502), `leg2End` (2519). `correctionStartIndex = 9`.

### F2 — Bearish mirror (`BEAR_MIRROR_FIXTURE`)

Deterministic mirror of F1 around 2559 (HIGH↔LOW swapped). Same magnitudes, `direction: BEARISH`. Proves the measurement is direction-symmetric and that the same C rule would hold for bullish and bearish source examples.

### F3 — Bearish nested-leg discriminator (`NESTED_LEG_FIXTURE`)

Source-shaped after the 1:02:41–1:03:32 worked example (outer leg containing its own 2Leg):

```text
parent Leg 1   2700 -> 2630  (70)
nested 2Leg    inside parent: 2700 -> 2667 (33), correction extreme 2692, 2692 -> 2659 (33), nested TP 2659
parent deep corr extreme      2658
parent Leg 2   2658 -> 2588  (70), parent TP1 2588
```

Asserts: parent magnitudes (70) ≠ nested magnitudes (33); nested TP (2659) ≠ parent TP1 (2588); parent Leg1 ≈ parent Leg2 and nested Leg1 ≈ nested Leg2 as equality *candidates only* (no tolerance, G6 separate).

### N1–N4 — Negative fixtures

| ID | Failure mode | Expected behavior |
|---|---|---|
| `NEG_NO_RANGE_FIXTURE` | no preceding range | `SPIKE_REQUIRES_CONTEXT_RANGE` → ineligible |
| `NEG_MISSING_STRUCTURAL_REFERENCE_FIXTURE` | no first-structural-low anchor | `ANCHOR_MISSING_FIRST_STRUCTURAL_LOW` (fail closed) |
| `NEG_C_BEFORE_CORRECTION_FIXTURE` | visual C placed at index 8 < correction start 9 | `LEG2_ORIGIN_CANNOT_PRECEDE_CORRECTION` |
| `NEG_NON_FINITE_FIXTURE` | NaN candle low | `CANDLE_GEOMETRY_MUST_BE_FINITE` (throw, never measure) |

## Mapping to the frame-request IDs

| Frame-request point | Fixture anchor it feeds |
|---|---|
| S1-A / S2-2 / S3-B (Leg 1 start) | `teacherPointA` |
| S1-B / S2-3 / S3-C (Leg 1 end) | `teacherPointB` |
| S1-C / S2-5 (correction extreme) | `correctionExtreme` |
| S2-4 (the "از اینجا" Leg 2 start) | `otherVisualPoint` (primary G5 visual candidate) |
| S3-A (deep leg start) | `otherVisualPoint` (the decisive C) |
| S3-D (pending limit) / S3-E (activation) | `pendingLimit` / `fill` — always reported `EXCLUDED_NON_CANONICAL` |
| S3-F (TP1) | Leg 2 end used for the G6 equality check |

## Usage protocol once the frames arrive

1. Fill the extracted coordinates into a fresh chart record (same anchor schema) with provenance (video time, frame, OHLC element).
2. Run `reportCandidates` / `measureLeg1` / `measureLeg2` on the extracted record.
3. Compare each family's Leg 1 magnitude against the teacher's implied Leg 1 (e.g. TP1 = Leg 1 projected from C). The family with the exact match is the source-consistent interpretation — the fixtures above prove the machinery can separate them.
4. If S3-A (deep leg start) ≠ S3-E (activation), record it as explicit source evidence that `fillPrice` is not the geometric `C` (identity separation invariant).
5. Only after a family/candidate is identified from source visuals may it be promoted to `SOURCE_CONFIRMED` and frozen — then fixtures for the frozen geometry replace these discriminating fixtures.

## Guardrails

- No canonical G4/G5 selection is made by this phase or its code.
- No historical XAUUSD data is consumed; all charts are synthetic.
- No equality tolerance, ATR/percentage/tick/point threshold, or buffer is introduced.
- `PENDING_LIMIT` and `ACTUAL_FILL` are execution concepts and stay excluded from canonical C.
- Fresh Holdout remains LOCKED; production Strategy A remains unchanged.

## Source-extraction input layer (schema + wiring)

`src/domain/research/sp2l-v2/G4G5SourceExtraction.ts` is the JSON-serializable provenance schema for the extracted frame coordinates and the input layer for the measurement helpers:

- `G4G5_SOURCE_POINT_REGISTRY` — canonical point IDs (S1-A…S3-F) with segment, category (LEG1_START / LEG1_END / CORRECTION / LEG2_END / EXECUTION / STRUCTURAL_SEQUENCE), gate (G1/G2/G4/G5/G6/NESTED_LEG), purpose, and the measurement anchor concept each point feeds.
- `ExtractedSourcePoint` — pointId, videoTime, candleTimestamp, price, OHLC element (or UNREADABLE), chart timeframe (M1/M5/UNKNOWN), direction (BUY/SELL/UNKNOWN), notes.
- `validateExtraction` / `assertValidExtraction` — fail-closed validation (unknown point ID, non-finite price, UNREADABLE-with-price, bad video time/timeframe/direction, missing video URL).
- `extractionToChart(extraction, segment)` — builds a `G4G5FixtureChart` whose anchors come only from readable points (UNREADABLE and sequence-count points stay in provenance but are excluded from measurement).
- `reportExtractionCandidates(extraction, segment)` — runs the G4/G5 measurements on the segment and reports `MEASURED`, `MISSING_EVIDENCE` (segment simply did not expose that anchor) or `INVALID_ORDER` per family/candidate, still without selecting a canonical one.
- `G4G5_EXTRACTION_TEMPLATE` — blank fill-in template matching the frame-request delivery sheet.

Tests: `tests/sp2l-v2-g4g5-source-extraction.test.ts` (11 tests) — validation errors, anchor mapping, end-to-end measurement with hand-computed magnitudes, UNREADABLE handling, SELL→BEARISH mapping, JSON round-trip, template validity.

## Files

- `src/domain/research/sp2l-v2/G4G5DiscriminatingFixtures.ts` — fixture data + mirror helper.
- `src/domain/research/sp2l-v2/G4G5CandidateMeasurement.ts` — measurement/report helpers (no selection).
- `src/domain/research/sp2l-v2/G4G5SourceExtraction.ts` — source-extraction schema + input layer.
- `tests/sp2l-v2-g4g5-discriminating-fixtures.test.ts` — 11 unit tests.
- `tests/sp2l-v2-g4g5-source-extraction.test.ts` — 11 unit tests.

## Validation

```bash
pnpm exec vitest run tests/sp2l-v2-g4g5-discriminating-fixtures.test.ts   # 11/11 pass
pnpm exec vitest run tests/sp2l-v2-g4g5-source-extraction.test.ts         # 11/11 pass
pnpm run build                                                            # tsc --noEmit clean
pnpm test                                                                 # 86/86 pass (full suite)
```