# SP2L F12 — Trigger Acceptance Source-Discrimination Fixture

Date: 2026-09-14  
Status: SOURCE-DISCRIMINATED for family existence; BLOCKED for final classifier  
Canonical status: NOT CANONICAL

## Purpose

F12 isolates the source-confirmed trigger family from the unresolved executable acceptance taxonomy.

This is a synthetic source-discrimination fixture, not historical evidence, optimization data, or a production rule. Source meaning outranks backtest performance.

## Source-aligned finding

The source evidence demonstrates one-, two-, and three-candle trigger constructions. Therefore a canonical rule that arbitrarily restricts Strategy A to exactly one candle is not source-aligned.

The fixture must still determine whether the source provides a unique deterministic classifier for accepting a one-, two-, or three-candle construction.

## Synthetic cases

Create three otherwise equivalent bullish SP2L-style constructions:

- **F12-A — one-candle trigger:** the trigger condition is represented by a single qualifying candle.
- **F12-B — two-candle trigger:** the same structural intent is expressed across two candles.
- **F12-C — three-candle trigger:** the same structural intent is expressed across three candles.

Each case preserves the surrounding source concepts: context/range, directional Spike, breakout/follow-through, correction, pending-Limit entry, and structural invalidation. No execution geometry is invented by the fixture.

Mirror constructions may be documented for bearish research only where source evidence supports them; absence of sufficient bearish evidence remains unresolved.

## Competing interpretations

### Candidate A — one-candle-only classifier

Accept only a single-candle trigger and reject multi-candle constructions.

### Candidate B — fixed two-candle classifier

Accept exactly two candles and reject one- and three-candle constructions.

### Candidate C — fixed three-candle classifier

Accept exactly three candles and reject one- and two-candle constructions.

### Candidate D — source-confirmed family

Permit one-, two-, and three-candle constructions, subject to additional source-defined conditions.

This candidate is currently supported at the family level, but the additional conditions are not yet deterministic.

### Candidate E — invented geometric classifier

Introduce arbitrary body/wick, size, percentage, timing, or threshold conditions to distinguish the three variants.

This is a negative control and must not be promoted without direct source evidence.

## Source-discrimination questions

1. Does the source explicitly establish acceptance of all three trigger lengths as valid constructions?
2. Does it define a unique candle-index or OHLC condition for each length?
3. Does it define equality, wick/body, minimum-size, or sequence thresholds?
4. Does it define a deterministic priority when multiple trigger constructions overlap?
5. Does it establish a universal bearish mirror?

## Adjudication

The source supports the existence of a one-/two-/three-candle family. It does not currently provide a sufficiently explicit deterministic classifier for the exact OHLC/candle-index acceptance conditions or overlap priority.

Therefore:

- **Family existence:** `SOURCE-DISCRIMINATED`
- **Final executable classifier:** `BLOCKED`
- **Overall F12 status:** `SOURCE-DISCRIMINATED` at semantic family level, `BLOCKED` at executable level.

No profitability or backtest comparison may be used to choose among the unresolved classifiers.

## Negative controls

Do not invent:

- a mandatory one-candle trigger;
- a mandatory two- or three-candle trigger;
- arbitrary candle-size thresholds;
- body/wick percentages;
- fixed pip/point thresholds;
- Fibonacci or ATR filters;
- arbitrary overlap priority;
- market-entry substitution for the source pending-Limit model.

## Gate impact

- SOURCE RESOLUTION: partial pass; trigger family established, executable classifier unresolved.
- SYNTHETIC FIXTURES: F12 explicitly defined.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED for Strategy A trigger geometry.
- UNTOUCHED VALIDATION: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: LOCKED.

## Governance

Documentation only. No engine, simulator, replay, or production changes. No backtest/optimization selection. Manual approval by Ali remains required for any future CANONICAL promotion.
