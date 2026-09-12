# G338 — Structural Anchor Event Source Audit

Date: 2026-09-12  
Parent gate: G337  
Source asset: user-supplied full SP2L lesson video + preserved transcript  
Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Objective

Determine whether the source explicitly identifies the structural event that selects the parent Leg-1 anchors before the measurement is drawn, in a way that can be converted into deterministic candle-level coordinates without discretionary reconstruction.

This gate is source-only. No historical performance, optimization, threshold fitting, or holdout data was used.

## Evidence reviewed

Primary worked-example interval: `01:02:41–01:04:32`.

Key source statements already established by G334/G336/G337:

- `01:02:52`: one segment is identified as Leg 1 and the following segment as Leg 2.
- `01:03:03`: a nested 2Leg is explicitly discussed.
- `01:03:19`: the larger move is treated as one leg and the subsequent larger move as another after a deep correction.
- `01:04:00`: the presenter says a deep leg can be waited for and identifies where that deep leg starts.
- `01:04:10`: seven lower highs are counted.
- `01:04:19`: the pending order is placed and then moved downward until activation.
- `01:04:32`: the presenter describes the measured first leg from the earlier identified deep-leg origin to the later endpoint and identifies the lower target as the R1 outcome, with R2 also possible.

Representative visual evidence:

| Frame | Time | SHA-256 | Structural observation |
|---|---:|---|---|
| F3761 | 01:02:41 | `ac4fa47c980ad64b97631accfcb84022773c9e4844ca28482e79186e45be41a5` | initial directional move and marked consolidation/range |
| F3773 | 01:02:53 | `00125a655f1cd246fdfb0ec9e81b8b433dc8d617a28e2cd5ebfb9d58621dfd9a` | structural/range context |
| F3779 | 01:02:59 | `0b3b0ce1d967e81bb1334fe38cfd7173f56e29ec18849679fce8cebd3bed17d0` | measurement over correction-related structure |
| F3859 | 01:04:19 | `a7aa9b16bffb3209a6ebab728fae0ab93f229fc7d6ec8f37638ab064b70593a6` | pending-limit marker at a lower-high area |
| F3868 | 01:04:28 | `91140cd04c7a84ce48f21e90ddb102d5626b2063def9cb99a8d9666faad3f4a0` | parent-leg measurement appears separately |
| F3869 | 01:04:29 | `a987b09cb58cbb04582bd85fd4905448a85d335f004e2e9022891a1b8cfc48b5` | stable parent-leg measurement |
| F3870 | 01:04:30 | `d57324d2d211e2a29412d8502f1059a01bd1745e2f880aee97a1ed979c593fe7` | separate correction/continuation measurement |
| F3872 | 01:04:32 | `f65aef8f98c5be98d6a4c9f59df96c05221c9fa07acbd8d0f49d1f5de50ed17d` | lower target / R1-R2 discussion |

## Findings

### 1. The source identifies a semantic anchor event: the deep-leg origin

The strongest new source bridge is verbal rather than numerical: at approximately `01:04:00`, the presenter explicitly identifies where the deep leg starts. Later, at `01:04:32`, he describes the measured Leg 1 as extending from that earlier deep-leg origin to the later endpoint.

This is stronger than merely saying that a leg exists. It establishes that the presenter has a specific structural origin in mind before measuring the parent leg.

However, the source still does not define the deep-leg origin as a deterministic candle event such as:

- highest high of a lookback window;
- lowest low of a lookback window;
- first candle after a breakout;
- candle open/close;
- wick extreme;
- a formally defined swing point.

Therefore the semantic event is source-supported, but its executable candle-selection rule remains unresolved.

### 2. The later Leg-1 endpoint is also semantically identified, but not algorithmically defined

At `01:04:32`, the presenter describes the parent Leg 1 from the earlier deep-leg origin to the later endpoint. The visual measurement confirms that a distinct endpoint is being used for the measured parent move.

The endpoint is therefore source-supported as a semantic object.

What remains absent is a rule that says exactly which candle field creates that endpoint. G337 already established that visual proximity does not justify choosing wick, body, open, or close semantics.

### 3. Seven lower highs are structural evidence for entry progression, not a definition of Leg-1 anchors

At `01:04:10`, the presenter counts seven lower highs. The subsequent frames show the pending-limit marker being moved downward through successive lower-high locations until activation.

This provides source-supported evidence that lower-high structure is relevant to execution timing/placement in this example.

It does **not** establish that:

`B = seventh lower high`

or:

`C = one of the lower highs`

or any fixed lower-high count rule.

The count is therefore retained as an example observation, not a canonical parameter.

### 4. Hierarchical/nested leg interpretation is source-confirmed

The earlier portion of the worked example explicitly distinguishes a nested 2Leg from the larger parent move. This matters because it demonstrates that the same price series can contain multiple leg scales.

Therefore an automated implementation cannot simply select the first visually obvious swing as A/B. It needs a source-confirmed rule for which structural scale is the parent leg.

The source currently provides the concept of a larger/deeper leg, but not a deterministic scale-selection algorithm.

### 5. The source still does not provide a machine-readable structural event

After combining the verbal bridge with the visual evidence, the source supports these semantic events:

`deep-leg origin` → `parent Leg 1` → `correction` → `pending-limit execution` → `Leg 2 / target`

But it does not supply a deterministic mapping such as:

`deep-leg origin = candle i where condition X holds`

or:

`Leg-1 endpoint = candle j field Y`

or:

`correction C = candle k field Z`.

No such formula should be invented from conventional technical-analysis terminology.

## Candidate structural-event models

| Candidate | Description | G338 status |
|---|---|---|
| S1 | Deep-leg origin is an explicitly identified source swing/origin | **source-supported semantic event; executable rule unresolved** |
| S2 | Leg-1 endpoint is the later source-identified endpoint | **source-supported semantic event; executable rule unresolved** |
| S3 | Seven lower highs define the parent leg | rejected as unsupported canonical inference |
| S4 | Seven lower highs define entry progression only | source-supported in this worked example; not a universal count rule |
| S5 | Parent scale is selected from the larger/deeper leg | source-supported concept; deterministic scale-selection rule unresolved |
| S6 | A/B/C are automatically highest/lowest OHLC extrema | not source-proven |
| S7 | A/B/C are conventional swing/fractal pivots | not source-proven |

## Important constraint added by G338

The source-resolution result can now be stated more precisely:

> The presenter does not appear to choose the parent Leg 1 from an arbitrary nearest swing. He refers to a specifically identified deeper-leg origin and later endpoint, and the worked example contains a hierarchical distinction between nested and larger legs.

This is useful source evidence, but it remains **semantic rather than executable**.

The implementation must therefore not silently convert `deep-leg origin` into a generic swing-high/swing-low algorithm.

## Consequence for A/B/C/D

The strongest current symbolic model is:

`A = source-identified deep-leg origin`

`B = source-identified later endpoint of parent Leg 1`

`C = source-identified correction reference`

`D = AB=CD completion`

Only the semantic roles above are source-supported. The exact OHLC/candle mapping remains unresolved, especially for C.

`C = fill_price` remains rejected as canonical.

## Gate decision

`G338 = PASS (semantic structural anchor event strengthened; executable candle rule unresolved)`

### Source ledger after G338

| Concept | Status |
|---|---|
| AB=CD concept | SOURCE-CONFIRMED |
| Leg2 ≈ Leg1 magnitude | SOURCE-CONFIRMED |
| Parent Leg 1 exists | SOURCE-CONFIRMED |
| Deep-leg origin as named/identified source event | SOURCE-SUPPORTED / STRENGTHENED |
| Parent Leg-1 endpoint as source-identified event | SOURCE-SUPPORTED |
| Nested vs parent leg hierarchy | SOURCE-CONFIRMED |
| Lower-high sequence relevant to entry placement | SOURCE-VISUAL SUPPORTED |
| Seven-lower-high count as universal rule | UNSUPPORTED |
| Exact A candle/price field | UNRESOLVED |
| Exact B candle/price field | UNRESOLVED |
| Exact C anchor | UNRESOLVED |
| Wick/body semantics | UNRESOLVED |
| `C = fill_price` | REJECTED AS CANONICAL |
| D projection formula | CONCEPTUALLY IMPLIED / EXECUTABLE FORM UNRESOLVED |
| AB=CD tolerance | UNRESOLVED |
| TP1 relationship to D | UNRESOLVED |
| TP2 relationship to D | UNRESOLVED |
| P-Gap executable geometry | UNRESOLVED |
| FROZEN_GEOMETRY | BLOCKED |
| DEV | BLOCKED |
| VALIDATION | PROTECTED |
| FRESH_HOLDOUT | NOT AUTHORIZED |
| PRODUCTION | BLOCKED |

## No implementation change

G338 is research documentation only.

No production strategy logic is changed.  
No P-Gap formula is changed.  
No target formula is changed.  
No historical backtest is run.  
No DEV/VAL/Fresh Holdout data is used to choose geometry.

## Next gate

The source bridge is now strong enough to justify a controlled **synthetic-fixture discrimination gate** rather than continuing to infer OHLC semantics from pixels indefinitely.

G339 should construct deterministic fixtures for the remaining source-compatible structural models — without declaring any one model canonical — and test whether each candidate can faithfully represent the source's semantic distinctions:

1. deep-leg origin separate from pending entry;
2. parent Leg 1 distinct from nested Leg 1;
3. correction distinct from fill;
4. second leg approximately equal to first leg;
5. AB=CD relationship preserved;
6. no invented wick/body or tolerance semantics.

Historical data must remain untouched for this stage.
