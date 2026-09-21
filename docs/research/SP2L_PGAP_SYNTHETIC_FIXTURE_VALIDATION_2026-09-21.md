# SP2L P-Gap Synthetic Fixture Validation — 2026-09-21

## Scope

This gate validates the reconstructed **adjacent-candle non-overlap primitive** extracted from the preserved Poursamadi source evidence. It does not validate a complete P-Gap classifier.

## Fixtures

| ID | Source-shaped case | Primitive expectation | Qualification |
|---|---|---:|---|
| PGAP-001 | breakout → continuation → gap | PASS | UNRESOLVED |
| PGAP-002 | higher lows → gap | PASS | UNRESOLVED |
| PGAP-003 | three-candle spike family | PASS | UNRESOLVED |
| PGAP-004 | overlap | REJECT | UNRESOLVED |
| PGAP-005 | equality | REJECT | UNRESOLVED |
| PGAP-006 | late / E-Gap-like extension | primitive PASS | UNRESOLVED |
| PGAP-007 | valid gap outside fixed legacy index window | primitive PASS | UNRESOLVED |
| PGAP-008 | bearish mirror | primitive PASS | UNRESOLVED |

## Result

**PRIMITIVE TEST GATE: PASS**

The fixture suite confirms that the reconstructed primitive can deterministically distinguish:

- strict non-overlap from overlap;
- strict non-overlap from equality;
- bullish and bearish geometric mirrors;
- a valid geometric gap that occurs outside the legacy fixed candle indices.

## Important limitation

A primitive-positive result is **not** a P-Gap classification.

The source says formation location and sequence matter, and explicitly describes multiple constructions. Therefore the following remain unresolved:

1. exact sequence/indexing and precedence;
2. deterministic definition of the early/strong trend context;
3. minimum gap size or price threshold;
4. exact breakout-level relationship;
5. deterministic separation of P-Gap from late/E-Gap-like extension;
6. universal qualification across all source variants;
7. independent bearish source demonstration in the preserved excerpt.

The suite therefore does **not** modify the existing forward-test detector and does not promote any rule to canonical geometry.

## Gate state

- Source reconstruction: PARTIAL / RESEARCH
- Adjacent-candle primitive: DISCRIMINATED
- Complete P-Gap detector: BLOCKED
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Production BUY/SELL authorization: DISABLED


## Qualification-layer reconstruction update

The preserved source provides enough wording to test two source-shaped qualification paths without freezing them as canonical:

- **Breakout → follow-through → P-Gap:** the teacher explicitly describes a breakout, a follow-through/key-bar, and P-Gap as the visual marker of the strong trend.
- **Higher-lows → P-Gap:** the teacher explicitly says higher lows can precede the gap and that this is treated as the same concept in the strategy.
- **Immediate-post-low variant:** the teacher describes a third three-candle movement variant, but the exact deterministic OHLC predicate is not recoverable from transcript wording alone; it remains unresolved.

A research-only observer was added to distinguish these source-shaped observations from the primitive gap event. It deliberately does not define a fixed candle count, fixed index, minimum gap size, or E-Gap cutoff.

### New gate result

**QUALIFICATION OBSERVATION GATE: PASS (research-only)**

The source-shaped variants can be represented and tested deterministically as observations. This does not mean the executable P-Gap detector is complete.

### Newly narrowed but still unresolved

- Breakout event can be represented as close beyond the prior high/low based on the teacher's explicit breakout wording, but exact candle indexing remains unresolved.
- Higher-low progression is source-described, but the required number of higher lows is not fixed.
- P-Gap remains location/context dependent; geometric non-overlap alone is insufficient.
- E-Gap separation is qualitative in the preserved excerpt (early/fast opportunity versus repeated extensions), not yet a deterministic numeric cutoff.
