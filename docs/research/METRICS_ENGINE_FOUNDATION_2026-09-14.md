# Metrics Engine Foundation — 2026-09-14

## Purpose

Provide deterministic descriptive statistics over realized trade outcomes without selecting, optimizing, or changing Strategy A rules.

## Metrics

- closed trades
- wins / losses
- win / loss rate
- total R
- average R
- median R
- expectancy R
- gross profit / gross loss in R
- profit factor
- maximum drawdown in R
- maximum consecutive losses

## Ordering

Drawdown and consecutive-loss calculations preserve the supplied trade order. The metrics layer therefore does not reorder trades to improve or otherwise alter the observed sequence.

## Source boundary

This component consumes realized outcomes only. It does not infer P-Gap, A/B/C/D anchors, entry fill semantics, structural stops, targets, sessions, or any other unresolved Strategy A geometry.

No parameter optimization is performed here.

## Next

Connect replay decisions to the execution simulator and metrics collector through a generic backtest runner, while preserving ambiguous OHLC events as unresolved rather than assigning an arbitrary outcome.
