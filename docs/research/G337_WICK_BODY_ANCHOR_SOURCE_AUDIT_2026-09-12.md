# G337 — Wick / Body Anchor Source Audit

Date: 2026-09-12  
Parent gate: G336  
Source asset: user-supplied full SP2L lesson video + preserved transcript  
Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Objective

Determine whether the source's own chart-drawing behavior establishes a deterministic convention for the price field used by Leg 1 / correction measurement anchors — specifically wick extreme, candle body open/close, or another structural reference.

This gate is source-only. No historical performance, optimization, threshold fitting, or holdout data was used.

The purpose is to distinguish **visible drawing alignment** from **source-confirmed semantic rules**. A pixel-level coincidence is not promoted to a canonical OHLC rule unless the source explicitly or consistently establishes that meaning.

## Evidence set

Primary worked-example interval: `01:02:41–01:04:32`.

Additional structural-example interval: `01:02:53–01:03:44` (representative frames inside the same worked example).

Representative frames inspected in this gate:

| Frame | Time | SHA-256 | Observation |
|---|---:|---|---|
| F3773 | 01:02:53 | `00125a655f1cd246fdfb0ec9e81b8b433dc8d617a28e2cd5ebfb9d58621dfd9a` | marked range / structural context |
| F3779 | 01:02:59 | `0b3b0ce1d967e81bb1334fe38cfd7173f56e29ec18849679fce8cebd3bed17d0` | vertical measurement object over correction-related structure |
| F3859 | 01:04:19 | `a7aa9b16bffb3209a6ebab728fae0ab93f229fc7d6ec8f37638ab064b70593a6` | pending-limit marker after lower-high sequence |
| F3868 | 01:04:28 | `91140cd04c7a84ce48f21e90ddb102d5626b2063def9cb99a8d9666faad3f4a0` | parent-leg measurement object |
| F3869 | 01:04:29 | `a987b09cb58cbb04582bd85fd4905448a85d335f004e2e9022891a1b8cfc48b5` | parent-leg measurement in stable visible position |
| F3870 | 01:04:30 | `d57324d2d211e2a29412d8502f1059a01bd1745e2f880aee97a1ed979c593fe7` | second measurement / correction-related rectangle |
| F3871 | 01:04:31 | `8a50db374defd08d16ac4430d8995cc94fa1dc93501d64dc76906e56ccef4a0c` | continuation / measurement |
| F3872 | 01:04:32 | `f65aef8f98c5be98d6a4c9f59df96c05221c9fa07acbd8d0f49d1f5de50ed17d` | lower target / R1-R2 discussion |

## Direct visual audit

### 1. F3869: the parent-leg measurement does not establish one uniform OHLC field

F3869 is useful because the red vertical measurement is stable enough to inspect against the underlying candles.

The visible upper endpoint is near the upper extreme of the local swing candle. The lower endpoint is near the lower part of the large bearish candle and visually closer to its body/close region than to the candle's lower wick extreme.

This creates an important source-resolution limitation:

- the upper endpoint can be visually described as **near a wick extreme**;
- the lower endpoint can be visually described as **near the body/close region**;
- the source does not label either endpoint as `high`, `low`, `open`, `close`, or another OHLC field;
- therefore the frame does **not** establish a single uniform wick-to-wick or body-to-body convention.

The observation is intentionally phrased as visual proximity, not as an exact coordinate claim.

### 2. F3868–F3869: the measurement object is not simply the pending-limit entry

The parent-leg measurement appears after the pending-limit marker is shown separately in F3859. Its geometry is materially distinct from the pending-order line.

This independently reinforces the G333/G334/G336 invariant:

`pending_limit_entry != automatically C`

and:

`parent Leg 1 geometry != pending-limit marker`

No wick/body conclusion may be derived by treating the fill price as one of the measurement endpoints.

### 3. F3870: another visible measurement does not rescue the convention

F3870 shows a separate red rectangle over the subsequent correction/continuation area. Its upper boundary is visually near the low region of the preceding large bearish move, while its lower boundary is visually near a later correction low.

Those boundaries appear compatible with structural/wick extrema, but the source does not label the object or state that its boundaries represent `low`, `close`, `C`, or another named OHLC field.

Therefore this frame provides supporting visual evidence that the presenter measures chart structure using price-level geometry, but it does **not** establish the executable OHLC field or a universal endpoint convention.

### 4. F3779: earlier measurement behavior is also insufficient to freeze semantics

F3779 contains another vertical measurement object associated with the worked example. Its endpoints are visually positioned around a swing-high / correction-low structure, but again there is no source label identifying the exact candle field used.

The same limitation remains:

- structural location is visible;
- exact OHLC semantics are not stated;
- no deterministic candle-index rule is supplied;
- no source tolerance is supplied for near-coincident wick/body boundaries.

### 5. No explicit wick/body statement was found in the audited source interval

The audited visual evidence does not contain a statement equivalent to any of the following:

- "use the wick high/low";
- "use the candle close";
- "use the candle open";
- "measure from body to body";
- "ignore wicks";
- "include wicks".

The source instead communicates the structure visually and verbally at the semantic level: deep-leg origin, later endpoint, correction, second leg, and AB=CD / Leg2≈Leg1.

That is enough to preserve the concept, but not enough to select an executable OHLC field.

## Candidate semantic models after G337

| Candidate | Description | G337 status |
|---|---|---|
| W1 | Parent Leg 1 anchors always use wick extremes | plausible, **not source-proven** |
| W2 | Parent Leg 1 anchors always use body open/close fields | plausible, **not source-proven** |
| W3 | One endpoint may use a wick and the other a body/close | visually compatible with F3869, **not established as a rule** |
| W4 | Anchors are structural price levels that may coincide with either wick/body depending on context | source-compatible, but exact structural selection rule unresolved |
| W5 | Anchors use the pending-limit fill | **rejected as canonical** by G333/G334/G336 |

No candidate is promoted to canonical production geometry.

## Source-first conclusion

G337 does **not** resolve wick-versus-body semantics.

The highest-confidence statement supported by the source is:

> The presenter measures meaningful directional/correction price structure directly on the chart, but the source does not provide a deterministic mapping from those visual endpoints to a specific OHLC field.

The visual evidence is therefore useful as a **constraint** against careless implementations, but it is not sufficient as a specification for an automated engine.

In particular, it would be invalid to freeze any of the following solely from these frames:

- `A = highest high`;
- `A = candle close`;
- `B = lowest low`;
- `B = candle close`;
- `C = correction wick extreme`;
- `C = correction body extreme`;
- any fixed tolerance between wick and body;
- any candle-count or swing-detection rule.

## Impact on AB=CD implementation

The source-confirmed semantic relationship remains:

- `AB = CD` is explicitly taught;
- Leg 2 is expected to approximately match Leg 1 in magnitude;
- a correction separates the legs;
- the entry order is a pending limit during the correction;
- the pending entry is not automatically the geometric C point.

But executable geometry still requires unresolved inputs:

1. exact A anchor field;
2. exact B anchor field;
3. exact C anchor;
4. deterministic D projection;
5. equality tolerance;
6. relationship of D to TP1/TP2.

G337 does not change any of those unresolved statuses.

## Gate decision

`G337 = PASS (visual anchor behavior audited; wick/body convention remains unresolved)`

### Source ledger after G337

| Concept | Status |
|---|---|
| AB=CD concept | SOURCE-CONFIRMED |
| Leg2 ≈ Leg1 magnitude | SOURCE-CONFIRMED |
| Parent Leg 1 exists | SOURCE-CONFIRMED |
| Parent Leg 1 semantic origin/endpoint | SOURCE-SUPPORTED |
| Exact A candle/price field | UNRESOLVED |
| Exact B candle/price field | UNRESOLVED |
| Exact C anchor | UNRESOLVED |
| Wick/body semantics | **UNRESOLVED** |
| Mixed wick/body convention | VISUALLY COMPATIBLE, NOT SOURCE-PROVEN |
| `C = fill_price` | REJECTED AS CANONICAL |
| D projection formula | CONCEPTUALLY IMPLIED / EXECUTABLE FORM UNRESOLVED |
| AB=CD tolerance | UNRESOLVED |
| TP1 relationship to D | UNRESOLVED |
| TP2 relationship to D | UNRESOLVED |
| R1/R2 fixed multiples | UNSUPPORTED |
| P-Gap executable geometry | UNRESOLVED |
| FROZEN_GEOMETRY | BLOCKED |
| DEV | BLOCKED |
| VALIDATION | PROTECTED |
| FRESH_HOLDOUT | NOT AUTHORIZED |
| PRODUCTION | BLOCKED |

## No implementation change

G337 intentionally changes research documentation only.

No production LegProjection logic is changed.  
No TP logic is changed.  
No P-Gap formula is changed.  
No historical backtest is run.  
No DEV/VAL/Fresh Holdout data is used to select geometry.

## Next highest-value source-resolution target

The remaining highest-value source question is no longer simply "wick or body?" It is whether the source ever explicitly identifies the **structural anchor selection event** that precedes the measurement — e.g. a named swing, deep-leg origin, correction extreme, or candle close — in a way that can be mapped to an exact chart object without discretionary reconstruction.

If the source does not provide that bridge, the project should stop source-resolution for this geometry at `UNRESOLVED` and move only to synthetic fixtures for competing hypotheses as **research-only candidates**, without promoting any hypothesis to the frozen production specification.
