# SP2L Strategy A V2 — Research Contract

**Branch:** `research/sp2l-strategy-a-v2-2026-09-27`  
**Status:** RESEARCH ONLY — NOT CANONICAL

## Purpose

V2 is a controlled research implementation of a fully specified SP2L-style execution contract so that the unresolved behavior in the source-aligned Strategy A research can be tested as a reproducible hypothesis.

V2 is deliberately isolated from the source-aligned detector. A V2 result must not promote or modify Frozen Geometry.

## V2 contract

### 1. P-Gap

For BUY:

`Low(after-spike) > High(before-spike) + 1.0`

For SELL:

`High(after-spike) < Low(before-spike) - 1.0`

The 1.0 price-unit threshold corresponds to the reference implementation's 100 broker points on a 0.01-point XAUUSD instrument.

### 2. Setup geometry

For BUY, the three setup candles are:

- before-spike: bullish
- spike: bullish
- after-spike: bullish
- closes and opens progress upward across the three candles
- spike body > 1.5 × before-spike body
- spike body > 1.5 × after-spike body
- P-Gap condition above

SELL is the exact OHLC mirror.

### 3. Trigger / Entry

After the setup candle, scan forward.

BUY trigger/entry:
- first candle where `current Low < previous Low`
- entry price = that current candle Low

SELL trigger/entry:
- first candle where `current High > previous High`
- entry price = that current candle High

If the first qualifying trigger produces non-positive risk or risk above 10.0 price units, the setup is rejected, matching the reference contract.

### 4. Stop and target

SL:
- BUY: Low of the candle before the Spike
- SELL: High of the candle before the Spike

TP:
- 1.0R

Maximum accepted base risk:
- 10.0 XAUUSD price units

Second entry:
- disabled in V2

### 5. Intrabar ambiguity

V2 intentionally closes the OHLC ambiguity with the following explicit mechanical convention:

If a live trade's M1 candle touches both SL and TP:
- **SL is assumed to occur first**
- the trade is recorded as a loss

Therefore V2 produces no AMBIGUOUS outcome for this condition. This is an implementation assumption, not source-confirmed chronology.

### 6. Filters intentionally disabled

V2 baseline does **not** use:

- EMA
- ATR
- ADX/range filter
- trend-structure filter
- session filter
- second entry

The purpose is to isolate geometry + trigger + SL/TP + SL-first OHLC handling.

## Provenance / internal research note

The V2 contract was reconstructed from a publicly accessible GitHub implementation used as an external research comparator during the 2026-09-27 SP2L audit. The external implementation reported a 65.17% result in its notebook, but that result is conditional on its own geometry, entry logic, filters, and SL-first OHLC convention.

This note is intentionally kept in the research documentation so the project can later identify why V2 exists and reproduce the experiment. V2 code and naming are otherwise independent of that external implementation.

External source audited:
`AlirezaSadabadi/PythonTraderBot`, SP2L Advanced Backtest notebook.

## Interpretation rule

A positive V2 backtest is evidence only for the V2 implementation contract on the tested MT5 data. It is **not** evidence that the contract is canonical Strategy A.

A weak/negative V2 result does not prove Strategy A is invalid; it only rejects or weakens this particular implementation hypothesis.

## Next gate

1. Run the V2 MT5-local replay on the same 2026-09-14 through 2026-09-25 XAUUSD window.
2. Record signal count, completed trades, win rate, net R, PF, DD, and direction split.
3. Compare V2 signal/entry timestamps against the prior source-aligned research run.
4. Do not optimize V2 parameters before this first controlled replay.
5. If V2 does not explain the observed discrepancy, return to SOURCE RESOLUTION rather than tuning filters.
