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

## P-Gap vs E-Gap timing reconstruction

Additional preserved-source evidence narrows the distinction:

- At 50:09, the teacher describes taking the opportunity early in the trend / quickly as P-Gap rather than E-Gap.
- At 50:26, the teacher links a valid setup to a broken prior high plus a sufficiently good trend, while saying it has not progressed far enough toward E-Gap.
- At 50:56–51:07, the teacher says after one extension, then another, and a third, the probability of E-Gap becomes high and the entry is avoided.

This supports a timing/extension dimension for P-Gap vs E-Gap. It does not provide a deterministic numeric cutoff, nor does it prove that one extension alone is the universal E-Gap boundary.

A research observer now records:
- early-trend when a geometric gap is observed with zero prior extension events;
- repeated-extension when a geometric gap is observed after one or more prior extension events;
- unresolved otherwise.

This is an evidence-preserving representation, not an executable classifier.

### Gate result

**P-GAP / E-GAP TIMING OBSERVATION GATE: PASS**

The source distinction can be encoded as an auditable observation axis. The executable P-Gap/E-Gap cutoff remains unresolved.

## Breakout → follow-through boundary refinement

The preserved transcript also gives a more specific source-shaped breakout observation at 31:02–31:29: a candle closes beyond the relevant level, and the next candle (follow-through/key bar) cannot return/overlap the prior breakout area. The source contrasts this with a return/overlap that would instead create a channel-like concept.

A research-only observer now records this two-part observation. The exact boundary for "return", exact candle indexing, and its relationship to the later P-Gap event remain unresolved.

**Result: PASS — source-shaped breakout/follow-through observation added; no canonical rule promoted.**

## Context-matrix gate

Added PGAP_EGAP_CONTEXT_MATRIX with six source-preserving classes:
1. early P-Gap-shaped;
2. late / repeated-extension E-Gap-shaped;
3. identical gap geometry with context intentionally separated;
4. no-gap control;
5. overlap control;
6. equality control.

The matrix demonstrates an important reconstruction constraint: identical adjacent-candle gap geometry does not by itself determine P-Gap versus E-Gap. Context/timing must remain an explicit input to qualification.

**Result: PASS — context is now represented separately from geometry.**

## Remaining blocker

No deterministic extension count, trend-age threshold, distance-from-origin threshold, or E-Gap cutoff has been inferred. Therefore the matrix remains observational and cannot promote a canonical P-Gap detector.

## Leg-1 structural boundary gate

Source visual evidence (Window A 36:30–37:26) supports Leg 1 as a structural swing-to-swing movement followed by correction and a second directional leg. The visual source does not uniquely identify whether the endpoints use open/close, wick extremes, or another structural field.

A research-only anchor hypothesis matrix now keeps three families separate: first-spike open → last-spike close; spike extremes; and structural swing endpoints. Bullish/bearish mirrors are included. None is canonical.

**Result: PASS — anchor hypotheses are isolated without silently promoting the existing implementation.**

The existing `LegProjection.ts` formula remains quarantined as research-stage and is not changed by this work.

### Current Leg-1 blocker

Exact A/B endpoints, wick/body semantics, and AB=CD tolerance remain unresolved. Therefore no Leg-1 formula may enter Frozen Geometry.


## AB=CD source-reconstruction gate

The preserved visual source explicitly labels the SP2L construction `AB=CD` and shows Leg 1 → correction → Leg 2 with approximate magnitude equality. It does not uniquely resolve the exact A/B/C/D price fields or a numerical equality tolerance.

A research-only matrix now covers three competing anchor families (structural swings, spike extremes, candle OHLC fields), bullish/bearish mirrors, exact equality, near-equality, and materially unequal cases. The matrix deliberately records tolerance as `UNRESOLVED` and every fixture remains `canonicalEligible: false`.

**Result: PASS — AB=CD hypotheses are discriminated without inventing a tolerance.**

### Canonical blocker remains

No A/B/C/D anchor family or numerical AB=CD tolerance is promoted. `LegProjection.ts` remains quarantined research code. Frozen Geometry remains BLOCKED and the forward test remains untouched.


## F08/F09/F15 fixture gate

Added research-only matrices for swing selection, entry geometry, and bearish geometry. The matrices distinguish competing hypotheses and preserve the source-evidence asymmetry for bearish P-Gap. All observations are explicitly noncanonical.

**Result: PASS — no unresolved hypothesis is promoted to executable geometry.**


## F11/F12 execution gate

Added joint trigger/lifecycle fixtures and counterexamples. Touch, breach, close, and fill are deliberately separate events. Pending-order replacement, cancellation, timeout, and fill outcomes remain research observations only.

**Result: PASS — no trigger or lifecycle semantics are promoted to canonical execution.**


## Geometry dependency gate
F08/F09/F10/F14 are now tracked as a dependency graph. Dependencies are observations only; no geometry is promoted and Frozen Geometry remains BLOCKED.
