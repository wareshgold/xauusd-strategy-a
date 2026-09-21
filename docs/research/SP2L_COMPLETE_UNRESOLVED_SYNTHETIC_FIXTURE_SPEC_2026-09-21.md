# SP2L Strategy A — Complete Unresolved Synthetic Fixture Specification
## 2026-09-21

Status: RESEARCH-ONLY / NON-CANONICAL

## Purpose

The final primary-source sweep returned `NO_NEW_EXECUTABLE_PRIMARY_SOURCE_EVIDENCE`. Frozen Geometry therefore remains BLOCKED.

This specification converts the remaining source ambiguities into deterministic synthetic test states. The fixtures are designed to prove that the implementation:

- preserves ambiguity instead of silently choosing a rule;
- rejects unresolved geometry from canonical signal generation;
- keeps competing interpretations distinguishable;
- separates geometry events from execution events;
- never promotes a backtest-preferred interpretation into a source rule.

A fixture PASS means only that the software represents and guards the state correctly. It is NOT evidence that the represented rule is teacher-confirmed.

## Source boundary

Canonical promotion requires primary-source evidence sufficient to specify every required input, boundary, index/order, threshold, event semantic, direction, and precedence.

No fixture in this document supplies those missing values.

## Fixture conventions

Each fixture must include:
- fixture_id
- feature
- synthetic candle/order state
- competing interpretations
- expected deterministic state
- forbidden inference
- expected canonical eligibility

Canonical eligibility is `false` for every unresolved fixture.

---

## F08 — Structural Correction / Swing Selection

### F08-001 — First Low vs Later Higher Low
Create one valid-looking bullish structure where:
- initial correction Low = L1;
- later correction creates higher Low = L2;
- L2 != L1;
- both remain structurally observable.

Expected:
- expose both candidate references;
- selector state = `UNRESOLVED`;
- no automatic latest/original choice.

### F08-002 — No Later Higher Low
Same structure but no later candidate.

Expected:
- original candidate remains observable;
- universal-selection status still depends on source definition;
- no promotion of a universal selector.

### F08-003 — Equal Candidate Lows
Create two candidate lows with identical price.

Expected:
- deterministic tie state;
- no hidden first/last/timestamp preference unless explicitly configured as a non-canonical test parameter.

### F08-004 — Bearish Lower-High Candidates
Create independent bearish LH candidates.

Expected:
- candidates remain distinct;
- no bullish-to-bearish symmetry is inferred.

---

## F09 — Entry Geometry

### F09-001 — Original/Base vs Latest Structural Entry
Create identical structure where:
- original/base reference price = E0;
- later HL/LH reference = E1;
- E0 != E1.

Expected:
- both candidate Entry anchors represented;
- Entry = `UNRESOLVED`;
- no signal eligible for canonical execution.

### F09-002 — Entry Field Ambiguity
Represent same candle with materially different:
- High;
- Low;
- Open;
- Close;
- wick/body level.

Expected:
- field identity remains explicit;
- no automatic OHLC selection.

### F09-003 — Entry Update Ambiguity
Create a pending order followed by a new structural reference.

Expected:
- state records old Entry and new candidate Entry;
- update policy = `UNRESOLVED`;
- no automatic move/retain behavior.

### F09-004 — Precedence Ambiguity
Provide two simultaneously valid entry references.

Expected:
- precedence = `UNRESOLVED`;
- no priority such as latest > original unless source confirms it.

---

## F10 — Stop Geometry

### F10-001 — Spike Wick vs Body
Construct spike where wick extreme and body extreme differ.

Expected:
- both anchors observable;
- SL anchor unresolved.

### F10-002 — Spike vs Structural Reference
Construct spike extreme different from base/structural swing.

Expected:
- competing stop anchors preserved.

### F10-003 — Structural vs Fixed-Distance Stop
Construct identical entry with:
- structural invalidation stop;
- fixed-distance candidate stop.

Expected:
- both represented;
- no risk-budget selection.

### F10-004 — Spread Isolation
Run geometry with spread = 0 and separately with non-zero spread.

Expected:
- geometry result does not silently absorb spread;
- spread remains execution-layer data unless source explicitly promotes it to geometry.

### F10-005 — Stop Refresh
After a structural update, create old SL and a new candidate SL.

Expected:
- refresh event represented;
- whether SL actually moves remains unresolved.

---

## F11 — Pending Order Lifecycle

### F11-001 — Pending Placement
Create a structure producing a research pending-order candidate.

Expected:
- state = `PENDING_ORDER`;
- pending is distinct from active position.

### F11-002 — Next Candle Structural Change
Change the reference on the next candle.

Expected:
- state exposes `STRUCTURAL_UPDATE`;
- delete/retain/replace remains unresolved.

### F11-003 — Delete Cause Ambiguity
Provide:
- structural change;
- unchanged structure;
- elapsed candles.

Expected:
- delete cause is separately represented;
- no inferred causal predicate.

### F11-004 — Timeout Ambiguity
Test 1, 2, 3, and longer waiting periods.

Expected:
- elapsed-candle count is observable;
- no timeout rule is asserted.

### F11-005 — Replacement Ambiguity
New candidate Entry/SL differs from existing order.

Expected:
- old and new orders remain traceable;
- replacement threshold and precedence unresolved.

### F11-006 — Fill Semantics
Create price-touch, price-breach, and bar-close states.

Expected:
- touch, breach, close, activation, and fill are separate event types;
- no touch=fill assumption.

### F11-007 — Bearish Lifecycle
Create independent SELL-side pending lifecycle.

Expected:
- no synthetic bearish symmetry;
- lifecycle remains unresolved until primary source explicitly defines it.

---

## F12 — Trigger / Activation / Candle Family

### F12-001 — Touch vs Breach vs Close
Create identical structure with trigger price:
- touched intrabar;
- breached intrabar;
- closed beyond.

Expected:
- events remain distinct;
- trigger semantics unresolved.

### F12-002 — Trigger vs Activation
Create pending order where a structural trigger occurs but order activation is represented separately.

Expected:
- trigger != activation by default.

### F12-003 — Activation vs Fill
Create activation and fill as separate synthetic events.

Expected:
- no automatic equivalence.

### F12-004 — 1/2/3 Candle Family
Create three deterministic synthetic constructions corresponding only to the source's stated one/two/three-candle family.

Expected:
- each construction is addressable;
- exact mapping remains `UNRESOLVED` unless source evidence later defines it.

### F12-005 — Trigger Precedence
Create multiple trigger candidates on the same structure.

Expected:
- precedence = `UNRESOLVED`;
- no 1 > 2 > 3 assumption.

---

## F13 — 2X

### F13-001 — 2X Label Without Coordinate
Represent 2X with no numerical price binding.

Expected:
- 2X exists as a source concept;
- exact price = unresolved.

### F13-002 — Half-Target Candidate
Create a state where half-target is a plausible candidate but not source-confirmed.

Expected:
- candidate stored as hypothesis only;
- never canonical.

### F13-003 — TP1/TP2 Binding
Create 2X with independent TP1 and TP2 levels.

Expected:
- relationships are explicit data;
- no automatic binding.

### F13-004 — R Binding
Create Entry/SL and calculate R only as an observational metric.

Expected:
- calculation cannot promote 2X geometry.

---

## P-Gap — Executable Geometry

### PG-001 — Pressure Boundary Ambiguity
Create identical visible gap with multiple plausible pressure/compression start points.

Expected:
- boundary candidates remain distinct;
- no fixed candle count.

### PG-002 — Gap Endpoint Field Ambiguity
Represent candidate endpoints using High/Low/Open/Close/body/wick.

Expected:
- endpoint fields remain unresolved.

### PG-003 — Indexing Ambiguity
Use the same candles under multiple indexing conventions.

Expected:
- indexing convention is explicit metadata;
- no fixed -4/-3/-2/-1 promotion.

### PG-004 — Threshold Ambiguity
Create gaps below, at, and above several synthetic thresholds.

Expected:
- threshold is a test dimension only;
- no threshold selected by performance.

### PG-005 — Bullish/Bearish Independence
Create independent BUY and SELL gap candidates.

Expected:
- no mirrored formula is generated automatically.

### PG-006 — Order-Space Boundary
Create gap and surrounding price space with multiple plausible order-space intervals.

Expected:
- order-space boundaries remain unresolved.

---

## F14 — AB=CD

### F14-001 — A/B/C/D Anchor Ambiguity
Create multiple candidate anchors on the same visible structure.

Expected:
- all candidates traceable;
- no automatic A/B/C/D selection.

### F14-002 — Price Field Ambiguity
Represent anchors using wick/body/OHLC alternatives.

Expected:
- field remains explicit and unresolved.

### F14-003 — Observed vs Projected D
Create:
- observed D;
- projected D;
- incomplete D.

Expected:
- completion state distinguishes all three.

### F14-004 — Equality Tolerance
Create Leg2 deviations around exact Leg1 equality.

Expected:
- deviation is measurable;
- no tolerance is selected or optimized.

---

## F15 — Bearish Geometry

### F15-001 — Explicit-Symmetry Guard
Create bullish geometry and a mathematically mirrored bearish candidate.

Expected:
- bearish canonical eligibility remains false;
- mirrored construction is tagged `SYNTHETIC_ONLY`.

### F15-002 — Bearish Entry/Stop Field Ambiguity
Create independent SELL candidates with differing High/Low/wick/body anchors.

Expected:
- field remains unresolved.

### F15-003 — Bearish Lifecycle
Create Sell Limit, trigger, delete, replace, activation, and fill as independent synthetic states.

Expected:
- no source claim is attached to any event.

---

## Round-Level — Executable Geometry

### ROUND-001 — Round Level Presence
Create a round-number level near a candidate structure.

Expected:
- level may be represented observationally;
- no execution effect.

### ROUND-002 — Round-Level Threshold
Create levels around multiple round-number distances.

Expected:
- threshold remains unresolved;
- no optimization-derived value.

### ROUND-003 — Round-Level Binding
Create a structure both with and without a nearby round level.

Expected:
- signal eligibility must not change unless a source-confirmed rule exists.

---

## Cross-feature safety fixtures

### SAFETY-001 — Any unresolved geometry
At least one required canonical feature is unresolved.

Expected:
- canonical eligibility = false;
- production BUY/SELL generation = blocked.

### SAFETY-002 — Backtest pressure
Provide a hypothetical backtest result favoring one competing interpretation.

Expected:
- selected canonical interpretation remains unresolved;
- performance cannot alter source status.

### SAFETY-003 — Implementation pressure
Provide an existing implementation that uses a fixed formula.

Expected:
- implementation is classified as implementation evidence only;
- source status remains unchanged.

### SAFETY-004 — Symmetry pressure
Provide a complete bullish rule and incomplete bearish evidence.

Expected:
- bearish rule remains unresolved.

### SAFETY-005 — Touch/fill pressure
Provide price-touch and successful fills in historical examples.

Expected:
- touch != fill unless explicitly source-confirmed.

---

## Acceptance Gate

The synthetic-fixture phase is complete only when:

1. Every unresolved blocker has at least one executable ambiguity fixture.
2. Every fixture has deterministic expected behavior.
3. No fixture promotes a rule to canonical.
4. Unresolved geometry cannot produce production BUY/SELL.
5. Trigger, activation, and fill are represented as separate concepts.
6. Bullish and bearish geometry remain independently source-gated.
7. P-Gap remains source-blocked despite any implementation formula.
8. AB=CD remains source-blocked on exact anchors/tolerance.
9. 2X remains source-blocked on exact binding.
10. Fixture PASS is explicitly documented as representation/guard validation, not source confirmation.

## Exit condition

If all fixtures pass:

- Synthetic Fixture Gate = PASS
- Frozen Geometry = STILL BLOCKED
- Canonical Geometry = UNCHANGED
- Untouched Validation = LOCKED
- Robustness/Stability = LOCKED
- Fresh Holdout = BLOCKED
- Production = DISABLED

No live trading authorization is implied.
