# SP2L Trigger Synthetic Fixture Specification — 2026-09-27

## Purpose

These fixtures isolate trigger semantics without selecting a canonical interpretation. They are deterministic research fixtures and MUST NOT be used to choose a trigger rule by backtest performance.

## Fixture matrix

| ID | Semantic isolated | BUY construction | SELL construction | Status |
|---|---|---|---|---|
| T1 | Immediate correction | first correction reaches reference Low | first correction reaches reference High | unresolved |
| T2 | Delayed reach | first correction misses; later candle reaches reference Low | first correction misses; later candle reaches reference High | unresolved |
| T3 | Exact touch | correction Low equals reference Low | correction High equals reference High | unresolved |
| T4 | Penetration | correction Low moves below reference Low | correction High moves above reference High | unresolved |
| T5 | Close-only distinction | close relation differs from extreme relation | close relation differs from extreme relation | unresolved |
| T6 | Multi-candle correction | several correction candles precede reach | several correction candles precede reach | unresolved |

## Required candidate interpretations

A. immediate next-candle + touch/penetration
B. immediate next-candle + close
C. scan-forward + touch/penetration
D. scan-forward + close

These are research labels only, not Strategy A rules.

## Acceptance criteria

Each fixture must make the intended semantic distinction observable from raw OHLC alone. Tests may report whether a candidate interpretation triggers, which candle triggers, and which reference candle is used.

Tests MUST NOT infer source-canonical trigger semantics, fill semantics, entry price, or production order behavior.

## Promotion gate

No fixture result may modify the V2 research contract, source-aligned detector, or production execution code.

Frozen trigger geometry remains blocked until primary-source evidence resolves the ambiguity.

Current stage: SOURCE RESOLUTION → SYNTHETIC FIXTURES
