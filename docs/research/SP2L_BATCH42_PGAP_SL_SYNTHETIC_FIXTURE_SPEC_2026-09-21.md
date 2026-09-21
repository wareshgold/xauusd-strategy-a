# SP2L Batch 42 — P-Gap Candidate + SL Synthetic Fixture Specification

Date: 2026-09-21

## Purpose

Create deterministic research fixtures for:

1. the non-canonical P-Gap Candidate V1 state machine;
2. the newly reported teacher SL clarification: spike shadow/wick plus spread.

These fixtures are engineering validation only. They do not freeze Strategy A
geometry and do not authorize production signals.

## Fixture contract

### P-Gap candidate

The candidate sequence is:

`PRESSURE_WINDOW -> PAUSE/COMPRESSION -> DIRECTIONAL_TREND_BAR -> CANDIDATE`

Parameters are explicit and configurable:

- pressure length: 10–30 candles;
- pause length: research parameter;
- compression range threshold: research parameter;
- trend-bar body threshold: research parameter;
- directional close requirement: research parameter.

The fixture suite must prove:

- valid bullish sequence is detected;
- valid bearish mirror is detected;
- fewer than 10 pressure candles is rejected;
- more than 30 pressure candles is rejected when the selected fixture
  configuration enforces the bounded source window;
- missing compression is rejected;
- non-directional trend bar is rejected;
- range-bound pressure is rejected;
- boundary values are deterministic.

### SL shadow + spread

For a bullish spike:

`SL = spike.low - spread`

For a bearish spike:

`SL = spike.high + spread`

Fixtures must prove:

- bullish uses the spike lower shadow/wick extreme;
- bearish uses the spike upper shadow/wick extreme;
- spread is added in the protective direction;
- spike body values cannot accidentally replace wick extremes;
- zero spread is deterministic;
- fractional/tick-size values remain explicit rather than silently rounded.

## Explicit unresolved execution semantics

These fixtures intentionally do NOT decide:

- bid/ask trigger side;
- spread snapshot timing;
- broker stop-level restrictions;
- tick-size rounding;
- slippage;
- whether an additional fixed safety buffer exists.

Those remain separate execution-layer questions.

## Promotion rule

Passing these fixtures means only:

**RESEARCH IMPLEMENTATION INTERNALLY CONSISTENT**

It does not mean:

**SOURCE-CONFIRMED CANONICAL GEOMETRY**

Frozen Geometry remains blocked until source requirements are satisfied.
