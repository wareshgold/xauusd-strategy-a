# G336 — AB=CD Anchor Semantics Audit

Date: 2026-09-12
Parent gate: G335
Source asset: user-supplied full SP2L lesson video + preserved transcript
Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

## Objective

Determine whether the worked source example provides enough evidence to freeze exact executable A/B/C/D anchors for the AB=CD relationship, without inventing candle-level semantics.

This gate is source-only. No historical performance, optimization, or parameter fitting was used.

## Evidence set

Primary worked-example interval: `01:02:41–01:04:32`.

Representative inspected frames:

| Frame | Time | SHA-256 | Purpose |
|---|---:|---|---|
| F3761 | 01:02:41 | `ac4fa47c980ad64b97631accfcb84022773c9e4844ca28482e79186e45be41a5` | initial structural context / marked range |
| F3859 | 01:04:19 | `a7aa9b16bffb3209a6ebab728fae0ab93f229fc7d6ec8f37638ab064b70593a6` | pending-limit marker after lower-high sequence |
| F3868 | 01:04:28 | `91140cd04c7a84ce48f21e90ddb102d5626b2063def9cb99a8d9666faad3f4a0` | parent-leg measurement annotation |
| F3871 | 01:04:31 | `8a50db374defd08d16ac4430d8995cc94fa1dc93501d64dc76906e56ccef4a0c` | continuation / measurement |
| F3872 | 01:04:32 | `f65aef8f98c5be98d6a4c9f59df96c05221c9fa07acbd8d0f49d1f5de50ed17d` | lower target annotation / R1-R2 discussion |

Earlier source evidence independently establishes that `AB=CD` is explicitly taught and that Leg 2 is expected to match Leg 1 in magnitude. The source-frame manifest records that the teaching frame does not expose executable A/B/C/D price coordinates. fileciteturn147file0

## Direct visual findings

### 1. Parent Leg 1 is visually measurable, but its candle-level semantics are not labelled

In the later worked-example frames, the source displays a red vertical measurement over a bearish move. The upper endpoint is materially earlier/higher than the pending-limit marker shown in the preceding frame. This confirms that the presenter is measuring a parent directional leg independently of the eventual execution marker.

The visual tool itself does not identify whether the measurement endpoint is:

- an extreme wick;
- candle body close/open;
- a structural swing coordinate;
- another source-specific chart point.

Therefore the visual measurement cannot by itself freeze wick/body semantics.

### 2. The pending-limit marker is a separate execution object

F3859 shows the short red horizontal pending-order marker at a lower-high area after the sequence of lower highs has developed. F3868 then shows the parent-leg measurement whose upper anchor is materially above that marker.

This reinforces the source-supported invariant from G333/G334:

`pending_limit_entry != automatically C`

and:

`parent Leg 1 geometry != pending-limit marker`

The source therefore does not justify using the eventual fill as the AB=CD C point merely for implementation convenience. fileciteturn163file0

### 3. A and B can be described only as visual candidate anchors

For the bearish worked example, the source supports a candidate structure of:

`A = earlier deep-leg origin`

`B = later endpoint of the parent Leg 1`

because the presenter verbally identifies the deep-leg start and later describes the measured Leg 1 from one earlier chart location to another. However, the transcript does not encode exact candle indices or OHLC fields for those locations.

Thus:

- semantic A/B existence: **source-supported**;
- exact candle indices: **unresolved**;
- wick/body selection: **unresolved**;
- numerical price values: **not source-extractable from transcript alone**.

### 4. C remains unresolved

The source clearly contains a correction between the first and second legs and separately contains a pending-limit entry during that correction. But the worked example does not explicitly label one unique point as `C`.

The following are all still possible source interpretations and cannot be discriminated from the available evidence:

- correction extreme;
- structural correction origin;
- a source-specific point inside the correction;
- pending-limit price;
- another chart reference not encoded in the transcript.

G333/G334 already provide strong evidence **against** simply setting `C = fill_price`.

Therefore `C = fill_price` is explicitly rejected as a canonical rule.

### 5. D / AB=CD completion is conceptually present, but not numerically executable

The source explicitly teaches `AB=CD` and identifies completion of the second leg. The worked example also identifies a target associated with R1 and an alternative R2 outcome.

But no source passage reviewed in this gate provides all of the following simultaneously:

1. exact A price;
2. exact B price;
3. exact C price;
4. exact D formula;
5. wick/body semantics;
6. equality tolerance;
7. precedence between AB=CD completion and TP1/TP2 reward labels.

Consequently an implementation such as:

`D = C + (B - A)`

would be a mathematically natural representation of AB=CD, but **not yet a source-frozen executable rule** because A, B, and C are not uniquely source-defined.

## Candidate anchor models

| Candidate | Description | Status |
|---|---|---|
| A1 | A/B are extreme wick points of parent Leg 1; C is correction extreme | plausible, not source-proven |
| A2 | A/B are body/open-close points; C is correction extreme | plausible, not source-proven |
| A3 | A/B are structural swing coordinates; C is a structural correction point | source-compatible, exact semantics unresolved |
| A4 | C equals pending-limit fill | **rejected as canonical by source evidence** |
| A5 | D is a direct AB=CD projection from uniquely identified A/B/C | conceptually valid, but inputs unresolved |

No candidate is promoted to production geometry in G336.

## Important source-first distinction

The source has now given us a useful two-layer model:

### Layer 1 — semantic geometry

- directional parent Leg 1 exists;
- correction follows it;
- second leg follows correction;
- Leg 2 approximately equals Leg 1;
- AB=CD is the named relationship.

### Layer 2 — executable coordinates

Still unresolved:

- exact A candle/price field;
- exact B candle/price field;
- exact C point;
- exact D projection formula in implementation terms;
- equality tolerance;
- TP1/TP2 relationship to D.

This distinction prevents the research implementation from accidentally converting a correct concept into an incorrect formula.

## Cross-check against earlier source work

Earlier source work independently concluded that exact Leg 1 endpoints remained TBD and that selecting endpoints from historical performance would violate the source-first protocol. fileciteturn157file0

The visual triangulation record likewise states that AB=CD is a magnitude relationship rather than a fully specified four-point algorithm, and explicitly marks arbitrary swing anchors, `C = entry`, fixed Fibonacci extensions, and invented tolerances as unsafe. fileciteturn158file0

G335 further established that R1/R2 are source reward/target outcomes but do not supply a fixed executable R-multiple formula. fileciteturn155file0

## Gate decision

`G336 = PASS (anchor candidates classified; no executable A/B/C/D model uniquely source-confirmed)`

### Source ledger after G336

| Concept | Status |
|---|---|
| AB=CD concept | SOURCE-CONFIRMED |
| Leg2 ≈ Leg1 magnitude | SOURCE-CONFIRMED |
| Parent Leg 1 exists | SOURCE-CONFIRMED |
| Parent Leg 1 A/B semantic candidates | SOURCE-SUPPORTED |
| Exact A candle/price field | UNRESOLVED |
| Exact B candle/price field | UNRESOLVED |
| Exact C anchor | UNRESOLVED |
| `C = fill_price` | REJECTED AS CANONICAL |
| D projection formula | CONCEPTUALLY IMPLIED / EXECUTABLE FORM UNRESOLVED |
| AB=CD tolerance | UNRESOLVED |
| Wick/body semantics | UNRESOLVED |
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

G336 intentionally changes **research documentation only**.

No LegProjection production logic is changed.
No TP logic is changed.
No P-Gap formula is changed.
No historical backtest is run.
No DEV/VAL/Fresh Holdout data is used to select geometry.

## Next source-resolution target

The next highest-value investigation is to discriminate the remaining anchor candidates using additional exact source frames, especially the moments where the presenter draws or moves the measurement/target objects. The goal is not to estimate coordinates from pixels as a substitute for source semantics, but to determine whether the presenter visibly uses a specific candle extreme/body/reference line consistently enough to establish the missing OHLC rule.

If no such source bridge exists, the correct result is to keep executable geometry unresolved rather than manufacture a deterministic rule.
