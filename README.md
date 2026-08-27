# XAUUSD Strategy A

Deterministic XAUUSD price-action signal system based on SP2L (Spike 2 Leg).

## Status

Project foundation. Strategy implementation has not started.

## Strategy

**Strategy A = SP2L**

Core concept:

`Spike → Correction → Leg 2`

The system is intended to detect explainable setups candle-by-candle, validate them with historical data, and only then publish live signals.

## Principles

- Deterministic, rule-based decisions.
- No AI-generated BUY/SELL decisions.
- No lookahead bias.
- No arbitrary thresholds when the specification is incomplete.
- Quality over signal frequency.
- Risk management is separated from strategy detection.
- Telegram is an output adapter, not part of the strategy core.
- GitHub/cloud infrastructure is the source of truth; the project must not depend on a personal/local computer.

## Planned pipeline

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
Telegram Adapter
```

## Validation-first workflow

```text
Hypothesis
   ↓
Implementation
   ↓
Backtest
   ↓
Metrics
   ↓
Validation
   ↓
Accept / Reject
```

The project will not optimize or deploy based on intuition alone.

## V1 scope

M1, M5, OHLC, market structure (HH/HL/LH/LL), breakout, follow-through, spike, P-GAP, correction, Leg 1, Leg 2, entry, structure-based SL, TP1, setup quality, basic risk, no-lookahead processing, and backtest logging.

Leg 3, fast scalping, advanced channel strategy, complex session strategy, AI prediction, machine learning, and automatic optimization are out of scope for V1.

## Data

Initial research candidate: Twelve Data XAU/USD. M1 is intended to be the raw source of truth; M5 should be derivable locally from M1 so candle boundaries remain deterministic.

API credentials must never be committed to this repository.

## Documentation

See `docs/strategy-a.md` for the authoritative Strategy A / SP2L specification.
