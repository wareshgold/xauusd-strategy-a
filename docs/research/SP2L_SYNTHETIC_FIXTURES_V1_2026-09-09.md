# SP2L Synthetic Fixture Discrimination Suite v1 — 2026-09-09

## Purpose

Discriminate competing geometric interpretations without using historical profitability. Fixtures are intentionally synthetic and deterministic.

## Fixture families

### F01 — P-Gap vs generic three-candle imbalance

Construct candle sequences where a conventional three-candle imbalance exists but the source-defined P-Gap visual condition is absent; and the converse where the source's demonstrated P-Gap condition is present without a generic FVG-style gap.

Expected status: no production classifier until source geometry is frozen. The fixture must expose both interpretations rather than silently selecting one.

### F02 — Fixed first Low vs relevant/current higher-low entry

Create a bullish spike followed by multiple higher lows. Place candidate pending-limit levels at:
- original/first structural Low;
- latest relevant higher Low;
- arbitrary midpoint.

The expected fixture output is a comparison record, not a trading decision. This directly tests the ambiguity observed in source frames around the moving Buy Limit line.

### F03 — Entry vs Leg-2 start

Create a setup where the correction entry level and the start of the projected Leg 2 are intentionally different. A valid implementation must preserve both coordinates and must not alias them.

Expected: `entry_price != leg2_start` is representable.

### F04 — AB=CD anchor alternatives

Construct A/B/C/D candidates under several plausible pivot definitions. Use the same OHLC sequence but vary only anchor interpretation. Expected output: all candidate projections are retained with provenance; no tolerance is applied because the source tolerance is unresolved.

### F05 — Wick extreme vs candle-body edge

Construct candles where the wick extreme and body edge differ materially. Candidate entry/stop anchors must remain distinct fields. No implementation may collapse them until source evidence resolves the anchor.

### F06 — Structural invalidation and order replacement

Create a pending order, then introduce a later candle that changes the relevant structural distance to invalidation. The fixture must model `KEEP`, `DELETE`, and `REPLACE` as explicit states. The exact material-change threshold remains unresolved and must not be guessed.

### F07 — Overextension / late-entry condition

Construct a clean setup and a visually similar setup where price has already extended substantially before the trigger. Expected: both are represented; the latter cannot be automatically rejected until the source's precise rule is frozen.

### F08 — Range interior vs breakout context

Construct identical local candle patterns once inside a range and once after a valid breakout. This tests that context is a first-class input and prevents a local pattern from becoming sufficient by itself.

## Required fixture record

Every fixture should serialize:

- fixture_id
- OHLC sequence
- timeframe
- intended source concept
- competing interpretations
- expected invariant
- observed engine output
- pass/fail
- provenance reference

## Gate rule

Fixtures are a source-resolution tool. They must be completed before historical optimization. A fixture failure is a specification/implementation problem, not a reason to change the fixture to obtain a better backtest.
