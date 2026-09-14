# SP2L F11 — Pending-Order Refresh Source-Discrimination Fixture

Date: 2026-09-14
Status: SOURCE-DOES-NOT-DISCRIMINATE
Canonical status: NOT CANONICAL

## Purpose

F11 isolates the unresolved rule governing whether a pending Limit order is retained, replaced, or otherwise refreshed when new structural candles form before the correction reaches the order.

This is a synthetic source-discrimination fixture. It is not historical evidence, optimization data, or a production execution rule.

## Source-aligned invariant

The source evidence supports a pending-Limit correction-entry model and directly permits order management to respond when additional structure develops. Visual/transcript evidence demonstrates that a prior order can be deleted and a new order placed when another candle forms and the relevant distance changes.

What remains unresolved is the deterministic condition for retaining versus replacing the order.

## Synthetic case

Construct a bullish sequence with:

1. Spike and breakout/follow-through;
2. a completed higher-low that establishes a candidate pending Buy Limit;
3. an unfilled correction phase;
4. a subsequent completed higher-low before price reaches the pending order;
5. a second subsequent structural update before fill.

Create mirrored research cases only where source evidence supports them; do not assume a universal bearish mirror.

## Competing interpretations

### Candidate A — retain original order

Once the pending Limit is placed, retain it until filled, cancelled by explicit invalidation, or otherwise explicitly terminated by source-defined logic.

### Candidate B — replace on every new relevant structural swing

When a new relevant higher-low/lower-high forms before fill, delete the prior pending order and place a new order at the newly relevant level.

### Candidate C — replace only when a qualitative/material-distance condition is met

Refresh is permitted, but only when the new structure materially changes the Entry-to-Stop relationship or another qualitative condition described by the source is satisfied.

This candidate is source-aligned semantically but is not yet deterministic because no numerical threshold has been established.

### Candidate D — fixed numerical replacement threshold

Replace the pending order when price/structure changes by a fixed pip, tick, percentage, ATR, or other numerical threshold.

This is not canonical unless the source explicitly provides such a threshold.

### Candidate E — market-entry replacement

Cancel the pending order and enter on candle-close/reclaim confirmation instead.

This is a negative control because it substitutes a market-trigger model for the source-confirmed pending-Limit correction-entry model.

## Source-discrimination questions

1. Does the source require retaining the original pending order after a new relevant structural swing?
2. Does it require replacement on every new relevant swing?
3. Does it explicitly define a qualitative/material-distance condition for replacement?
4. Does it provide a numerical replacement threshold?
5. Does it ever replace pending-limit execution with market entry?
6. Is the refresh rule universal across bullish and bearish variants?

## Current adjudication

The source discriminates against Candidate E: market-close/reclaim entry is not a valid replacement for the pending-Limit model.

The source supports the existence of refresh/replacement behavior, but does not uniquely discriminate among retaining the original order, replacing on every relevant swing, or applying a qualitative/material-distance condition.

No numerical threshold is source-confirmed.

Therefore:

`SOURCE-DOES-NOT-DISCRIMINATE`

at the deterministic retain/replace level.

## Negative controls

Do not invent:

- a pip/tick replacement threshold;
- an ATR threshold;
- a percentage threshold;
- a fixed number of candles after which the order must move;
- a requirement to move on every swing without source confirmation;
- market-entry-on-close as a substitute for pending Limit;
- a universal bearish mirror.

## Gate impact

- SOURCE RESOLUTION: partial pass; refresh semantics narrowed but not deterministic.
- SYNTHETIC FIXTURES: F11 explicitly defined.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED for Strategy A geometry/execution semantics.
- UNTOUCHED VALIDATION: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: LOCKED.

## Governance

No engine changes are authorized by this fixture. No backtest result may select a candidate. Any future canonical refresh rule requires direct source evidence and explicit manual approval by Ali.
