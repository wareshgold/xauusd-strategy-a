# Strategy A / SP2L Specification

## 1. Identity and objective

**Strategy A = SP2L (Spike 2 Leg).**

The objective is to convert the SP2L price-action concept into a deterministic, explainable system that can detect setups candle-by-candle, calculate entry/SL/TP, score setup quality, log backtests, and eventually publish signals to Telegram.

Core concept:

**Spike → Correction → Leg 2**

The strategy seeks to capture the second leg after a powerful initial move.

## 2. Core principles

- Spike is evidence of power, not an entry by itself.
- Pattern and context must be evaluated together.
- Market structure is more important than candle counting.
- HL/LH, P-GAP, Level, and 2L are not standalone signals.
- No setup may be forced when information is incomplete.
- Default decision under uncertainty is **NO TRADE**.
- Every setup has an invalidation condition and limited lifetime.
- Strategy detection, risk management, execution, and notification remain separate concerns.
- No lookahead bias is permitted.
- Quality is preferred over signal frequency.

## 3. Spike

A Spike is a powerful, relatively fast price movement, normally emerging from a range/compression or meaningful context. A large candle alone is not sufficient.

The detector must evaluate, as available from OHLC and derived structure:

- direction
- start and end
- movement size
- candle strength
- speed
- Higher High / Higher Low or Lower High / Lower Low structure
- breakout behaviour
- follow-through
- overlap
- P-GAP evidence
- location and context
- whether the move is clean or channel-like

A bullish Spike represents dominant buying pressure; a bearish Spike represents dominant selling pressure.

## 4. Breakout and follow-through

A breakout is stronger when price breaks meaningful structure and closes beyond it. A subsequent Follow Through candle should continue in the breakout direction and should not materially return into the prior structure.

The exact numeric thresholds are intentionally unresolved until they are formally defined and validated with data.

## 5. P-GAP

P-GAP (Pressure Gap) is a context-dependent imbalance associated with a powerful move. Not every visual gap is a P-GAP; E-GAP/common gaps must not automatically qualify.

The algorithm must eventually define P-GAP numerically. Until that definition is established, the implementation must not invent a threshold.

## 6. Spike variants

At minimum, the specification recognises two broad formation sequences:

### Variant A

Breakout + Follow Through, followed by clear HL/LH progression.

### Variant B

HL/LH progression first, followed by P-GAP and/or breakout.

These are variants of Strategy A, not separate strategies in V1. Architecture should allow future separation.

## 7. Anti-channel and market-quality filter

A move with excessive overlap, repeated internal corrections, alternating structure, or channel-like behaviour should not be forced into a Spike classification.

Clean examples include directional HL progression for bullish movement or LH progression for bearish movement. Dirty conditions include excessive alternation and overlapping, unclear structure.

Dirty or low-quality conditions should be rejected or assigned reduced quality/risk according to validated rules.

## 8. Correction and 2L

After a valid Spike, the system waits for the first meaningful correction.

The central pattern is:

`Leg 1 (A→B) → Correction → Leg 2 (B→C)`

The intended projection is approximately:

- BUY: `TP1 ≈ Entry + Leg1`
- SELL: `TP1 ≈ Entry - Leg1`

Two legs must be identified structurally; a fixed number of candles is not sufficient.

## 9. Entry and invalidation

For a bullish setup, correction may be recognised when price enters below the first important setup Low as defined by the eventual structural rules. For bearish setups, the inverse applies.

Entry may be represented as market or limit execution, but the exact algorithm is an unresolved item and must be validated before production.

SL is structure-based: it must sit at a point where reaching it invalidates the trade hypothesis, not at an arbitrary fixed distance.

## 10. Targets

TP1 is the primary target and represents completion of the projected Leg 2.

TP2 is optional and must not be treated as the primary expectation. Its exact definition remains subject to data validation.

Leg 3 is out of scope for V1.

## 11. 2X

2X / second position is a money-management/execution concept, not part of the core setup detector. It may use a better entry within the same validated setup and must remain separately configurable.

Exact 2X rules are unresolved for V1.

## 12. Context and location

The setup must be evaluated relative to market location and higher-level context. Relevant context may include:

- major structure
- significant highs/lows
- support/resistance
- breakout/retest areas
- range boundaries
- round numbers
- EMA/equilibrium context
- session timing

An EMA 60 on M1 is an educational example and may be used as a configurable equilibrium/context feature, not as an automatic entry trigger.

Round-number spacing and session windows must be configurable rather than hard-coded.

## 13. Multi-timeframe

V1 supports M1 and M5. Higher timeframes may later provide context while lower timeframes provide setup/entry structure. Exact timeframe roles must be validated rather than assumed.

## 14. Time and session context

London, Frankfurt, and New York sessions are relevant contextual factors. Session open can introduce volatility, gaps, new Spikes, or invalidation. Session windows and avoid windows must be configurable.

Complex session strategy logic is out of scope for V1; basic context fields may still be logged.

## 15. Quality scoring

Initial conceptual grades:

### A — High Quality

Clear Spike, clear breakout, good follow-through, P-GAP, clean structure, good location, appropriate timing, reasonable width, suitable equilibrium context.

### B — Medium Quality

Several positive factors but not an ideal setup. Risk may be reduced after validation.

### C — Low Quality

Dirty market, excessive overlap, wide/poor Spike, poor location, E-GAP context, late entry, or other materially adverse conditions. Default: no trade.

Numeric weights and thresholds are unresolved and must be established through hypothesis → implementation → backtest → validation.

## 16. Risk management

Risk is separate from signal detection. Setup quality may map to full, reduced, or zero risk only after validation. Minimum RR and sizing rules remain unresolved.

## 17. Signal output

A validated signal should be explainable and contain at least:

- Strategy: A / SP2L
- Direction: BUY / SELL
- Timeframe
- Entry
- Stop Loss
- TP1
- TP2 when applicable
- Leg 1
- Risk
- Setup Quality
- Confidence/quality representation
- Human-readable reason

No signal is emitted when required conditions are not satisfied.

## 18. V1 scope

Required:

- M1
- M5
- OHLC
- HH / HL / LH / LL
- Breakout
- Follow Through
- Spike
- P-GAP
- Correction
- Leg 1
- Leg 2
- Entry
- structure-based SL
- TP1
- setup quality
- basic risk
- no lookahead
- backtest logging

Out of scope:

- Leg 3
- fast scalping mode
- advanced channel strategy
- complex session strategy
- AI prediction
- machine learning
- automatic optimization
- nested SP2L

## 19. Critical unresolved rules

The following must not be guessed:

1. Numeric P-GAP definition.
2. Minimum HL/LH count.
3. Maximum Spike width.
4. Exact dirty-market definition.
5. Maximum acceptable candle overlap.
6. First important Low/High algorithm.
7. Exact entry algorithm.
8. Exact SL algorithm.
9. TP1/TP2 distinction.
10. Quality-score thresholds.
11. Round-level algorithm.
12. Session windows.
13. Minimum Leg 1 size.
14. Maximum Leg 1 size.
15. Minimum RR.
16. Exact 2X conditions.
17. Session-open gap handling.

Every unresolved rule follows:

`Hypothesis → Implementation → Backtest → Metrics → Validation → Accept/Reject`

## 20. Validation requirements

Backtesting must include at least 50 trades per meaningful variant and preferably 100+ where data permits. Logging should include entry, SL, TP1, TP2, result, R multiple, time, session, Spike size, Leg 1, Leg 2, P-GAP, EMA distance, location, market quality, and setup score.

Core metrics:

- win rate
- average R
- expectancy
- profit factor
- maximum drawdown
- average winner
- average loser
- TP1 hit rate
- TP2 hit rate
- SL rate
- consecutive losses
- session performance

Validation must actively seek failed Spikes, false breakouts, SL trades, dirty markets, wide Spikes, E-GAP cases, and late entries. The purpose is to find weaknesses, not merely confirm the hypothesis.

## 21. Decision sequence

The engine should conceptually ask:

`WHERE AM I? → WHAT HAPPENED? → WHO HAS POWER? → WHERE IS THE CORRECTION? → IS THERE A VALID 2L? → WHERE IS THE LEVEL? → HAS THE TRIGGER OCCURRED? → IS THE SETUP STILL VALID? → ENTRY`

## 22. Architecture boundary

The planned pipeline is:

```text
Market Data
     ↓
Candle Builder
     ↓
Structure Detector
     ↓
Spike Detector
     ↓
Breakout Detector
     ↓
P-GAP Detector
     ↓
Correction Detector
     ↓
Leg 2 Projection
     ↓
Location Filter
     ↓
Quality Scoring
     ↓
Risk Management
     ↓
Signal Generator
     ↓
Notification Adapter
```

The strategy core must not depend on Telegram, a particular broker, or Waresh Gold Assistant.

## 23. Data principle

Initial research provider candidate: Twelve Data XAU/USD. M1 is intended as the raw source of truth; M5 should be derived locally from M1 where practical. Raw market data must remain immutable and API credentials must never be committed.
