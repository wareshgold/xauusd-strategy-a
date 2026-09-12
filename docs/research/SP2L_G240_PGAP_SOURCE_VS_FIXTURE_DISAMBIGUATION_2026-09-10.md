# SP2L G240 — P-Gap source-vs-fixture disambiguation

**Date:** 2026-09-10  
**Gate:** SOURCE RESOLUTION → SYNTHETIC FIXTURES  
**Status:** `SOURCE_CORRELATED_CANDIDATE__NO_CANONICAL_GEOMETRY_FREEZE`

## Objective

Cross-map the G239 numeric fixture hypotheses against the strongest source evidence already recovered in G234–G236. The purpose is to determine which source-visible distinctions can actually be resolved, without using historical performance and without inventing visual measurements.

## Evidence boundary

This pass uses only the previously documented source observations:

- raw SP2L teaching sequence around 31:00–32:10;
- the SP2L P-GAP labeling in that teaching sequence;
- the positive/negative example panel around 35:50–36:16;
- the explicit `Valid BO = P-Gap` annotation;
- the same-author Gap-course endpoint description `High[t-2]` versus `Low[t]`;
- the G239 numeric fixture matrix.

No backtest result is used to decide source meaning.

## Source-to-fixture cross-map

| Source observation | G239 fixture implication | Resolution |
|---|---|---|
| Earlier candle and later candle are visually separated by one intervening spike/directional candle | Compatible with F1/F8 and the strict H1 candidate `High[t-2] < Low[t]` | Strong compatibility |
| Positive examples repeatedly show a qualifying shaded gap/separation | F6-style directional movement without qualifying separation is inconsistent with accepted examples | Qualitative negative evidence |
| Three positive examples share the same endpoint relationship | Supports the same three-candle indexing hypothesis across examples | Strong compatibility |
| Source visuals do not provide exact numerical wick/body endpoints | F2 cannot be rejected or accepted solely from the source panel | Unresolved |
| Source visuals do not show an exact equality/touch case | F3 cannot distinguish strict `<` from inclusive `<=` | Unresolved |
| Positive examples are not accompanied by a sufficiently explicit taxonomy label proving Breakout Gap | F4 vs F5 cannot be uniquely resolved as a production requirement | Unresolved |
| Intervening candle is described/illustrated as a spike or directional candle | F7 shows why a gap-only hypothesis may be insufficient, but source does not provide a numeric spike threshold | Candidate conjunction only |
| P-GAP is separately named in SP2L and is shown with `Valid BO` | Does not prove P-Gap equals Breakout Gap or Pressure Gap | Separation confirmed; equivalence unresolved |

## Fixture-by-fixture interpretation

### F1 — strict full-extrema separation

The strongest currently source-correlated hypothesis. The same-author Gap-course wording directly references the upper extreme of the earlier candle and lower extreme of the later candle, and the SP2L teaching sequence places one directional candle between them. This remains a **candidate**, not a frozen production predicate.

### F2 — body-only separation with wick overlap

The available source frames are not sufficiently precise to establish that candle bodies, rather than full extrema, define the P-Gap boundary. Keep as an explicit competing hypothesis. Do not reject it using visual estimation.

### F3 — exact-touch equality

No reviewed source example supplies a controlled equality/touch case. Therefore strict versus inclusive comparison remains unresolved. Do not choose `<=` merely because it increases fixture coverage.

### F4/F5 — generic gap versus breakout-context requirement

The source strongly associates P-Gap with valid breakout, but the available evidence does not prove that the additional Breakout-Gap taxonomy condition from the comprehensive Gap course is a mandatory P-Gap rule. In particular, a close-at-previous-high condition must not be imported without direct SP2L evidence.

### F6 — directional movement without qualifying gap

The rejected red-X example is qualitatively consistent with this negative control: directional movement alone is not sufficient for `Valid BO = P-Gap`. This strengthens the gap/separation requirement but does not identify the complete executable predicate.

### F7 — gap with weak/non-spike intervening candle

The source construction repeatedly depicts a directional/spike candle between the endpoint candles. That makes `gap + spike` a serious candidate conjunction. However, no deterministic spike-size/shape threshold is source-confirmed, so the project must not manufacture one.

### F8 — gap with explicit clear-spike/breakout annotation

Strongly compatible with the source teaching construction. It is useful as a positive synthetic control, but its explicit annotations are fixture metadata rather than source-derived numeric thresholds.

## Disambiguation result

The source evidence resolves the following at research level:

1. P-Gap is not merely any directional move.
2. P-Gap is associated with a qualifying gap/separation.
3. The relevant construction repeatedly uses an earlier candle, one intervening directional/spike candle, and a later candle.
4. `High[t-2] < Low[t]` is the leading source-correlated bullish endpoint hypothesis.
5. P-Gap must remain distinct from Pressure Gap; no evidence supports interpreting the `P` as Pressure.

The source evidence does **not** resolve:

- exact wick versus body semantics;
- strict versus inclusive equality;
- minimum gap distance;
- whether spike is a mandatory logical condition versus descriptive context;
- a deterministic spike magnitude/shape formula;
- whether Breakout-Gap taxonomy conditions are mandatory;
- exact bearish mirror;
- exact P-Gap event timing;
- exact shaded-region boundaries.

## Gate decision

**Source Resolution:** improved / still blocked for executable geometry.  
**Synthetic Fixtures:** PASS and useful for separating hypotheses.  
**Frozen Geometry:** **BLOCKED**.  
**DEV:** BLOCKED.  
**Untouched Validation:** PROTECTED / not authorized.  
**Fresh Holdout:** PROTECTED.  
**Production BUY/SELL:** BLOCKED.

## Next action

Do not backtest competing P-Gap formulas yet. Continue source resolution at the raw-video level, prioritizing a frame or sequence where the author explicitly points to the two P-Gap endpoints and the candle wicks are simultaneously visible at sufficient resolution.

If no stronger source evidence is recoverable, the next formal decision may record `High[t-2] < Low[t]` as the leading source-correlated candidate while preserving the unresolved semantics as explicit UNKNOWN fields rather than silently choosing them.
