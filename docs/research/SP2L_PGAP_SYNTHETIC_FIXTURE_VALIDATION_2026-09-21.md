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
