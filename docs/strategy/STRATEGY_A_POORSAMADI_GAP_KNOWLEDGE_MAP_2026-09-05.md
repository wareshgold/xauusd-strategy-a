# Strategy A — Poorsamadi Gap Knowledge Map

**Date:** 2026-09-05  
**Branch:** `research/strategy-a-poorsamadi-alignment`  
**Purpose:** Long-term research map for returning to Poorsamadi gap semantics and completing deterministic codification later.

## 1. Why this map exists

The Poorsamadi gap material contains semantic rules that are important to Strategy A but are not yet sufficiently numeric for direct implementation.

This document is a durable research index: future work should return here before implementing or modifying any gap-related rule.

**Rule:** source meaning first, deterministic codification second, historical validation third, production implementation last.

## 2. Core gap taxonomy

### P-GAP — Pressure Gap

**Meaning:** A gap/pressure movement associated with pushing the market directionally, including movements that help break a range or continue a directional structure.

**Role in Strategy A:** Evidence that can belong to the strong-movement / spike family.

**Current status:** SEMANTICALLY ESTABLISHED; exact geometry TBD.

**Do not assume yet:** fixed point size, body-only gap, wick-based gap, ATR threshold, overlap percentage, or mandatory candle count.

### Exhaustion Gap

**Meaning:** A gap occurring late in an already extended movement, especially when aligned with an important market location, where the pressure interpretation should no longer be treated as continuation pressure.

**Role:** Can become exit/reversal context rather than continuation-entry evidence.

**Current status:** SEMANTICALLY ESTABLISHED; exact deterministic detector TBD.

### Common / Other Gaps

The source distinguishes gap concepts beyond P-GAP and exhaustion gap. Their exact taxonomy and decision tree are not yet sufficiently specified for Strategy A implementation.

**Status:** TBD.

## 3. Context rules

Gap interpretation must be evaluated together with:

- timeframe;
- session / time of day;
- symbol/market;
- market location;
- trend/cycle context;
- position of the gap within the movement;
- whether the movement is beginning/continuing or reaching exhaustion.

Therefore:

`gap geometry alone != signal`

## 4. SP2L relationship

Current semantic model:

`RANGE / LOCATION`

`→ directional pressure / breakout`

`→ follow-through`

`→ strong-movement / SPIKE FAMILY`

`→ correction`

`→ pending limit entry`

`→ Leg2 ≈ Leg1`

P-GAP can be evidence inside the strong-movement family, but it is **not yet established as a universal mandatory condition for every SP2L spike branch**.

## 5. Pressure vs exhaustion decision problem

The key future research task is not merely "detect a gap". It is:

> Given a gap-like movement, determine whether the correct semantic interpretation is pressure/continuation or exhaustion/reversal, using only information available at that time.

Required inputs will likely include:

1. prior range/structure;
2. breakout status;
3. follow-through behavior;
4. directional sequence;
5. gap geometry;
6. location;
7. session/time;
8. trend/cycle state.

No future candle may be used in the live decision unless that future candle is actually the confirmation trigger defined by the rule.

## 6. Explicit TBD checklist

- [ ] Exact P-GAP geometric definition
- [ ] Exact Common-GAP / E-GAP classification
- [ ] Exact exhaustion-gap definition
- [ ] Body vs wick measurement
- [ ] Minimum gap size
- [ ] Gap tolerance / fill tolerance
- [ ] Required candle count
- [ ] P-GAP relation to breakout
- [ ] P-GAP relation to follow-through
- [ ] Structural location rule
- [ ] Session/time windows
- [ ] Trend/cycle dependency
- [ ] Entry trigger after P-GAP
- [ ] Exit/reversal trigger after exhaustion gap
- [ ] Stop placement
- [ ] Same-candle ordering
- [ ] Intrabar/touch semantics
- [ ] Historical positive/negative fixtures
- [ ] OOS validation protocol

## 7. Evidence already captured

### Lesson: Effect of different gap types at every chart location

User-supplied transcript, approximately 0:00–16:21.

Important source intervals:

- **0:00–0:53:** P-GAP and exhaustion gap are explicitly distinguished.
- **3:04–3:46:** a setup is not valid merely because the movement looks good; time/entry rules matter.
- **4:00–5:36:** pressure versus exhaustion interpretation and risk/stop-distance context.
- **6:08–7:51:** session context can change a gap from pressure interpretation to exhaustion interpretation; first signs of failure can justify exit.
- **8:17–9:48:** late movement at an important level is treated as exhaustion/reversal context.
- **14:19–15:16:** gaps near the end of a movement can behave as exhaustion, while gaps that break a range are described as pressure gaps.
- **15:44–16:13:** gap effect depends on session and market location; pressure gaps are used for entry and exhaustion gaps for exit/reversal context.

## 8. Research hypotheses — NOT canonical rules

These are allowed as research hypotheses only:

### H-GAP-01
P-GAP is more useful when it participates in a range-break / directional continuation sequence than when it appears late in an already extended movement.

### H-GAP-02
Exhaustion-gap behavior is more likely near important structural/round locations after multiple directional legs.

### H-GAP-03
Session context materially changes the conditional outcome of visually similar gap structures.

### H-GAP-04
A deterministic classifier combining geometry + sequence + location + session should outperform geometry-only classification.

These hypotheses must be tested without changing the canonical Strategy A until validated.

## 9. Research discipline

A future analyst must not:

- convert the teacher's examples into universal thresholds without evidence;
- optimize thresholds directly on the fresh holdout;
- use post-entry information to define an entry-time gap label;
- silently replace the canonical Strategy A detector;
- treat statistical significance as proof of economic edge;
- mix exploratory P-GAP experiments into production code.

## 10. Relationship to source documents

Semantic hierarchy:

1. `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt` — raw source.
2. `docs/strategy/STRATEGY_A_POORSAMADI_SOURCE_LEDGER.md` — semantic ledger.
3. `docs/strategy/STRATEGY_A_POORSAMADI_CODIFICATION_SPEC_V2_2026-09-05.md` — deterministic codification boundary.
4. This document — persistent gap-specific knowledge map.
5. Research reports — empirical tests of explicit hypotheses.
6. Production code — only after the research/implementation gate is passed.

## 11. Current conclusion

**P-GAP and exhaustion gap are now recorded as separate semantic concepts.**

The most important reusable principle is:

`A gap is not a signal by itself.`

Its interpretation depends on **where**, **when**, and **within what movement/structure** it appears.

The exact numerical gap detector remains open and must be resolved from additional source material or explicitly labeled research hypotheses before implementation.
