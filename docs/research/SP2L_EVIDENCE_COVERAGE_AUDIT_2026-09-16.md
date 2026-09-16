# SP2L Evidence Coverage Audit — 2026-09-16

## Purpose

Classify the existing primary-source evidence for each Frozen Geometry blocker by the highest level it actually supports, without promoting unresolved source meaning.

Coverage levels:

- `CONCEPTUAL`: establishes that the concept exists.
- `STRUCTURAL`: establishes sequence/relationship/behavior, but not enough executable precision.
- `EXECUTABLE`: uniquely determines the geometry/execution semantics required by the canonical contract.

`EXECUTABLE` coverage is required for `SOURCE_CONFIRMED`; conceptual or structural coverage alone cannot unlock the gate.

## Coverage matrix

| Field | Conceptual | Structural | Executable | Current state | Missing discriminator |
|---|---|---|---|---|---|
| `entry` | Yes | Yes | No | `PARTIAL` | Exact universal entry anchor and structural event; distinguish first entry from Leg-2 origin where applicable. |
| `invalidation` | Yes | Yes | No | `PARTIAL` | Exact OHLC/wick/body anchor and explicit buffer/offset semantics. |
| `limitRefresh` | Yes | Yes | No | `PARTIAL` | Deterministic refresh threshold/condition and resulting order action. |
| `trigger` | Yes | Yes | No | `PARTIAL` | Deterministic classifier, acceptance conditions, and precedence across one/two/three-candle and bar/key-bar variants. |
| `twoX` | Yes | Yes | No | `PARTIAL` | Exact 2X anchor, target-distance reference, sizing, stop, and fill semantics. |
| `abcd` | Yes | Yes | No | `PARTIAL` | Exact A/B/C/D anchors, measurement convention, and tolerance/non-equality rule. |
| `pGap` | Yes | Partial/Yes | No | `UNRESOLVED` | Unique OHLC formula, candle indexing, location constraints, and boundary versus E-Gap. |

## Evidence interpretation

### Entry

Primary transcript evidence establishes correction/Limit behavior and that an order can be placed within the initial three-candle structure. It does not uniquely expose a universal executable price formula.

### Invalidation

Primary transcript evidence establishes that return to the referenced level invalidates the scenario. It does not uniquely establish the precise OHLC anchor or any numerical buffer.

### Limit refresh

Primary transcript evidence establishes that later candle movement can change stop distance and may lead to deleting/replacing or retaining/moving an order. It does not establish the numeric or deterministic threshold.

### Trigger

Primary transcript evidence establishes a trigger family including one-, two-, and three-candle structures plus bar/key-bar variants. It does not establish a universal classifier or precedence rule.

### 2X

Primary transcript evidence establishes 2X as an optional later entry and supports the concept of approximately half-target positioning in the broader source material. It does not expose a universal formula, sizing, or fill model.

### AB=CD

Primary transcript evidence explicitly connects SPIKE-2LEG to AB=CD and states the second leg is expected to match the first. It does not uniquely define the A/B/C/D anchors or tolerance.

### P-Gap

Primary transcript evidence distinguishes P-Gap from E-Gap and associates P-Gap with breakout construction. It does not uniquely expose the required OHLC/index equation.

## Audit conclusion

No blocker currently has `EXECUTABLE` coverage.

Therefore:

- `SOURCE_CONFIRMED = 0/7`
- Frozen Geometry = `BLOCKED`
- Untouched Validation remains locked.
- Robustness/Stability remains locked.
- Fresh Holdout remains locked.
- Production remains off.

## Important distinction

This audit is not a ranking of which rule is "closest" to being solved. It is a classification of evidence coverage only. No field is promoted based on apparent completeness, implementation convenience, or backtest behavior.

## Evidence acquisition consequence

Future work should prioritize acquiring primary evidence that moves a field from `STRUCTURAL` to `EXECUTABLE`. New evidence must enter through the deterministic Evidence Intake Template and Register.

## Integrity

- No geometry changed.
- No execution rule invented.
- No BUY/SELL generated.
- 125R remains untouched, unmodified, unclipped, and unreclassified.
