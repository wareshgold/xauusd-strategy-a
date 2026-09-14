# SP2L Synthetic Source-Discrimination Fixtures F8–F15 — 2026-09-14

## Purpose

Define synthetic fixtures that discriminate competing source interpretations without selecting rules by profitability.

These fixtures are **non-canonical research artifacts**. They must not be treated as historical evidence, optimization data, or production geometry.

## Governance

- Source meaning outranks backtest performance.
- A fixture may eliminate an interpretation only when the source evidence actually distinguishes the behaviors.
- If source evidence does not discriminate a fixture, the result remains `UNRESOLVED`.
- No numerical tolerance, formula, anchor, buffer, or execution rule is invented by these fixtures.
- Manual approval by Ali is required before any rule can become `CANONICAL`.

## Fixture Matrix

| Fixture | Question | Competing interpretations | Required observation | Current gate |
|---|---|---|---|---|
| F8 | Which correction low governs pending entry? | first/base low; latest relevant HL/LH; immutable original order | Compare source examples with evolving higher-low sequence | BLOCKED — source discrimination required |
| F9 | Is Entry the start of Leg 2? | Entry = Leg-2 start; Entry distinct from Leg-2 start | Deliberately separate the two prices | BLOCKED |
| F10 | What is structural invalidation? | wick/base structural level; body level; risk-distance stop | Keep Entry and invalidation materially separate | BLOCKED |
| F11 | When is a pending order refreshed? | never; every new relevant swing; qualitative/material-distance replacement | Add a new structural low/high before fill | BLOCKED — threshold must not be invented |
| F12 | How are trigger variants accepted? | one-candle; two-candle; three-candle family | Same setup represented with 1/2/3 candle constructions | BLOCKED |
| F13 | What does 2X mean operationally? | half-target concept; second-position reward profile; other source interpretation | Keep interpretations numerically distinct | BLOCKED |
| F14 | Which points define AB=CD? | competing A/B/C anchors | Construct materially different projections from each anchor set | BLOCKED — no tolerance invented |
| F15 | Does geometry mirror bearish setups? | bullish-only asymmetry; mirrored bearish structure | Reflect F8–F14 where source evidence permits | BLOCKED |

## Fixture Construction Rules

### F8 — Dynamic relevant-low candidate

Create a bullish directional sequence with multiple completed higher lows before correction. Record each candidate pending-limit level independently. Do not assign a universal refresh threshold. Expected research output is an evidence comparison, not an engine decision.

### F9 — Entry versus Leg-2 start

Create a setup where the pending entry level and the structural beginning of the continuation leg are intentionally separated. Any implementation that silently equates them is marked as an interpretation requiring source support.

### F10 — Structural invalidation

Create separate entry, base structural low, relevant higher-low, and body/wick values. The fixture must prevent a risk percentage from determining the structural stop. Exact wick/body semantics remain unresolved.

### F11 — Pending refresh

Extend the structure after order placement and before fill. Record old and new candidate levels. The fixture must permit `UNRESOLVED` where the source does not provide a deterministic replacement condition. No arbitrary pip, percentage, ATR, or distance threshold is allowed.

### F12 — Trigger family

Represent one-, two-, and three-candle source examples independently. Do not collapse them into a single classifier until the source defines the acceptance taxonomy.

### F13 — 2X

Create numerically distinct half-target and second-position interpretations so that later source evidence can discriminate them without parameter optimization.

### F14 — AB=CD

Create multiple plausible A/B/C constructions that produce materially different D projections. Do not choose the projection with the best historical performance. No numerical equality tolerance is assigned here.

### F15 — Bearish mirror

Mirror the bullish fixture structures and compare only where the source provides direct or sufficiently strong evidence. Absence of bearish evidence must remain unresolved rather than being assumed symmetric.

## Required Result Vocabulary

Each fixture must eventually resolve to exactly one of:

- `SOURCE-DISCRIMINATED`
- `SOURCE-DOES-NOT-DISCRIMINATE`
- `BLOCKED`
- `REJECTED` — only with a documented source-based reason

`SOURCE-DOES-NOT-DISCRIMINATE` means the competing interpretations remain valid research hypotheses and cannot be canonicalized from the available evidence.

## Current Research Status

The existing source record strongly narrows Entry toward a dynamic/relevant higher-low in the demonstrated bullish example, keeps Entry separate from structural invalidation, confirms Pending Limit execution, and confirms AB=CD as a magnitude relationship. It does **not** yet provide enough evidence to freeze universal algorithms for F8–F15.

Therefore this fixture pack records the discrimination work without pretending that the unresolved geometry has been solved.

## Gate

**SOURCE RESOLUTION: IN PROGRESS**

**SYNTHETIC FIXTURES: DEFINED**

**FROZEN GEOMETRY: BLOCKED**

**DEV / VALIDATION / FRESH HOLDOUT / PRODUCTION: LOCKED**

## Next Action

Use the authoritative source transcript/visual evidence to adjudicate F8–F15 one fixture at a time. Only source-supported eliminations may change the geometry status. If ambiguity survives, preserve `UNRESOLVED` and continue source research.