# SP2L SOURCE RESOLUTION CHECKPOINT — 2026-09-26 — PRESSURE GAP CANDLE-MAPPING PASS

Branch: research/sp2l-f13-forensic-repro-2026-09-26

## New source evidence — P-Gap candle relationship

The primary SP2L transcript gives a more specific visual/candle-level description of P-Gap:

- At 34:14, P-Gap is presented as a practical marker for identifying the relevant breakout.
- At 34:25, the instructor describes the first case as a gap where the **high and low do not overlap**.
- At 34:35, the instructor explicitly says that in another case the gap is not present initially but **forms on the next candle**.
- At 34:44–35:02, two structural orders are treated as the same concept:
  1. breakout first, then higher lows, then P-Gap;
  2. higher lows first, then P-Gap.
- At 35:37, both cases are explicitly described as P-Gap cases.
- At 36:05, these are treated as valid spike variants.

This is stronger evidence than the earlier generic Gap statement because it is directly inside the SP2L lesson and explicitly names the structure as P-Gap.

## What this resolves

### P-Gap = Pressure Gap
SOURCE-CONFIRMED.

### Geometric property
A source-confirmed P-Gap example has a **non-overlap / separation between the relevant candle high and low**.

The source wording supports the geometric idea:

`relevant High < relevant Low`

with the directional mirror for the opposite side.

### Candle indexing
The new evidence shows that P-Gap **cannot yet be safely hard-coded to one universal fixed index such as t-2**.

The source explicitly presents two valid structural orderings:
- breakout → follow-through / higher lows → P-Gap
- higher lows → P-Gap

Therefore the previously considered generic relation:

`Low[t] > High[t-2]`

remains a **generic Gap candidate**, not the frozen SP2L P-Gap index formula.

## Important correction

The previous checkpoint statement that the base Gap formula was sufficient to define the P-Gap geometry is now narrowed.

Current source-aligned status:

- P-Gap identity: SOURCE-CONFIRMED
- P-Gap non-overlap property: SOURCE-CONFIRMED
- P-Gap exact candle pair/index: STILL UNRESOLVED
- P-Gap exact OHLC field mapping: PARTIALLY-CONFIRMED (high/low non-overlap), not fully indexed
- P-Gap bullish/bearish executable mirror: NOT YET SOURCE-VERIFIED
- Pressure context: SOURCE-DESCRIBED, deterministic Boolean still unresolved
- SP2L Spike mapping: PARTIALLY-CONFIRMED
- Frozen Geometry: BLOCKED

## Evidence boundary

Do NOT promote `Low[t] > High[t-2]` as the canonical SP2L P-Gap formula from the generic Gap lesson alone.

Do NOT restore the old candidate `low[1] > high[3] + 1`.

The next source-resolution target is now precise:
**identify the exact two candle roles represented by the non-overlapping High/Low pair in the SP2L P-Gap examples, including the delayed-P-Gap variant.**

No detector/backtest change is justified yet.


## Source-aligned research branch — 2026-09-26

A separate research branch now tests the **strict separation form without an invented numeric threshold**:

- BUY research condition: `correction.low > a.high`
- SELL research condition: `correction.high < a.low`
- Existing window: `a, spike, correction, trigger = [-5],[-4],[-3],[-2]`
- Therefore the research implementation tests the t vs t-2 relationship in that existing window.
- `p_gap_price=0.0` is the source-aligned threshold setting; positive values remain counterfactual sensitivity tests.

This branch is explicitly **RESEARCH-ONLY**. It does not claim that the SP2L source has frozen the universal candle index across all P-Gap variants. The source transcript explicitly describes more than one ordering in which P-Gap can appear.

The purpose of the next one-month MT5 replay is therefore:
1. quantify the effect of removing the unsupported +1 price threshold;
2. compare the source-aligned strict-separation candidate with the prior research implementation;
3. preserve all data/session/timestamp/fill caveats;
4. do NOT select the formula because it produces better backtest performance.

Production/live canonical promotion remains blocked until candle-role mapping is source-frozen.


## One-month MT5 replay result — 2026-09-26

User-run connected-terminal replay:
- Interval: 2026-08-26T00:00:00Z through 2026-09-25T23:59:59Z
- Requested base: XAUUSD
- Resolved symbol: XAUUSD.ecn
- M1 bars: 19,343
- Signals: 212
- Decisive outcomes: 115
- WIN: 28
- LOSS: 87
- Decisive WR: 24.3478%
- 95% Wilson CI: 17.4164% to 32.9377%
- Net R: -59
- Simplified PF: 0.3218
- Max DD: 59R
- Max consecutive losses: 11

Report:
artifacts/backtest-mt5-local/SP2L_MT5_LOCAL_MULTI_SYMBOL_20260926T083809Z.json

Interpretation:
- This is strong negative research evidence for the current strict-separation implementation over this one-month replay.
- It does NOT establish that the source Pressure Gap definition is wrong, because the exact SP2L candle-role mapping remains unresolved and the replay still has research-only session/fill/timestamp constraints.
- The result does not justify canonical promotion, live use, or selecting this formula by performance.
- Next required comparison is the same exact one-month interval with the prior research threshold (p_gap_price=1.0), followed by candidate-level diff; source resolution remains the deciding gate.
