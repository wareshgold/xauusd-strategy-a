# SP2L F13/F14 Multi-Gate Consolidation — 2026-09-22

## Objective
Advance F13 (2X) and F14 (AB=CD) together, using only source-supported claims and explicitly preserving unresolved geometry.

## F14 — AB=CD
### Source-confirmed
- SPIKE-2LEG is explicitly associated with 2Leg / AB=CD.
- The second leg is expected to match the first leg in magnitude.
- Nested leg hierarchies are demonstrated; an inner 2Leg must not automatically be treated as the outer Leg 1/Leg 2 pair.

### Still unresolved
- A endpoint;
- B endpoint;
- C endpoint;
- D/target endpoint;
- wick/body/structural-pivot measurement;
- equality tolerance;
- whether C is Entry, correction extreme, or another source-defined reference.

### Decision
F14 remains **SOURCE-CONFIRMED SEMANTICALLY / EXECUTABLE GEOMETRY UNRESOLVED**.

## F13 — 2X
### Source-confirmed
- 2X is an optional later/secondary position concept.
- One demonstrated example associates the 2X entry with approximately half-target progression.
- The examples distinguish the later position's own entry-to-target reward distance from the initial position.

### Independent implementation corroboration
The inspected author implementation uses a 50%-of-risk secondary entry and a 2.0 volume multiplier. This is useful corroboration, but implementation configuration cannot define canonical Strategy A semantics by itself.

### Still unresolved
- universal 2X activation predicate;
- whether half-target is always the activation reference;
- universal price equation;
- sizing/risk relationship;
- stop and fill lifecycle.

### Decision
F13 remains **SEMANTICALLY SUPPORTED / EXECUTABLE FORMULA UNRESOLVED**.

## Cross-gate discriminator
The current evidence does NOT justify any of the following as canonical:
- `C = Entry`;
- `C = Fill`;
- `TP1 = C ± Leg1Size`;
- Fibonacci extension as AB=CD;
- fixed numerical AB=CD tolerance;
- universal `2X = 50% of initial risk`;
- mandatory 2X activation at 0.5R or 50% of target.

## Synthetic fixture consequences
Add/retain discrimination fixtures for:
1. competing A/B/C endpoint definitions;
2. wick-vs-body measurement;
3. zero/strict/nonzero AB=CD tolerance;
4. nested inner versus outer 2Leg;
5. 2X optional versus mandatory;
6. half-target activation versus alternative source reference;
7. 50%-risk secondary entry versus other candidate formulas.

These fixtures are for source discrimination and regression protection, not parameter optimization.

## Gate summary
| Feature | Status |
|---|---|
| AB=CD magnitude relationship | SOURCE-CONFIRMED |
| A/B/C/D exact anchors | UNRESOLVED |
| AB=CD tolerance | UNRESOLVED |
| 2X optional concept | SOURCE-CONFIRMED |
| Half-target association | SOURCE-CONFIRMED FOR DEMONSTRATED EXAMPLE |
| Universal 2X formula | UNRESOLVED |
| Frozen Geometry | BLOCKED |
| Validation / Fresh Holdout | LOCKED |
| Production | OFF |

## Next action
Before any canonical geometry change, perform a final source-artifact availability audit for the specific frames/examples that could discriminate A/B/C/D and 2X activation. If no uniquely discriminating primary artifact exists, keep both gates unresolved and move to source-to-code reconciliation rather than selecting a best-fit formula.

No canonical production code changed.