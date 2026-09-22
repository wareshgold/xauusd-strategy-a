# SP2L P-Gap Geometry Resolution Gate — 2026-09-22

## Research action

A source-first search was performed against the repository history for P-Gap evidence, archived frame identifiers, and timestamped visual references.

Existing source-aligned records were rechecked against the research P-Gap implementation history.

## Evidence result

The repository history confirms:

- P-Gap is source-confirmed as the valid-breakout concept.
- P-Gap is distinguished from common/E-Gap.
- The historical `PGAPResearch.ts` implementation is explicitly non-authoritative and only detects a three-candle imbalance candidate.
- No repository-visible evidence found in this pass uniquely maps that heuristic to the teacher's P-Gap definition.
- Existing source triangulation explicitly keeps exact OHLC formula, candle indexing, and equality/boundary semantics unresolved.

Therefore the historical three-candle condition must remain **RESEARCH-ONLY**.

## Geometry decision

No P-Gap formula is promoted.

Specifically, this pass does **not** authorize:

- `right.low > left.high` as canonical bullish P-Gap;
- `right.high < left.low` as canonical bearish P-Gap;
- any fixed candle-index mapping;
- any +1 price/tick/pip threshold;
- any equality rule;
- any universal three-candle P-Gap model.

## Next discriminating evidence requirement

To pass the P-Gap geometry gate, the authoritative visual evidence must discriminate at least:

1. which candles/price boundaries are marked as the P-Gap;
2. which side of the boundaries is used;
3. whether equality is allowed;
4. whether the construction is tied to the Spike candle, breakout candle, or another source-defined reference;
5. whether the same geometry is demonstrated in both directional variants.

Until that evidence is available in an auditable form, Frozen Geometry remains blocked.

## Gate

- P-Gap semantics: **SOURCE-CONFIRMED**
- P-Gap executable geometry: **UNRESOLVED**
- Research heuristic: **NON-CANONICAL**
- Frozen Geometry: **BLOCKED**
- DEV/validation/holdout: **LOCKED**
- Production: **OFF**
