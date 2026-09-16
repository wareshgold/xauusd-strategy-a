# SP2L Pre-Freeze Backtest Audit — 2026-09-16

## Purpose

Record the current audit of the existing Strategy A baseline backtests without promoting them to canonical validation evidence.

## Evidence reviewed

- `data/reports/strategy-a-baseline/1min.json`
- `data/reports/strategy-a-baseline/5min.json`
- `scripts/run-baseline-backtest.ts`
- `src/backtest/BacktestEngine.ts`
- `src/backtest/BacktestTypes.ts`
- `src/domain/strategy-a/EntryTrigger.ts`
- `src/domain/strategy-a/Invalidation.ts`
- `src/domain/strategy-a/LegProjection.ts`
- `docs/research/SP2L_SOURCE_GEOMETRY_DECISION_MATRIX_V2_2026-09-09.md`

## Existing baseline metrics

| Timeframe | Candles | Closed trades | Wins | Losses | Win rate | Avg/Expectancy R | Profit Factor | Max DD R | Max consecutive losses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1min | 10,000 | 338 | 96 | 242 | 28.40% | +0.1208 | 1.1687 | 101.4471 | 15 |
| 5min | 10,000 | 241 | 78 | 163 | 32.37% | -0.1055 | 0.8440 | 36.7005 | 12 |

These are PRE-FREEZE / EXPERIMENTAL baseline metrics only. They are not canonical Strategy A performance.

## Metric-engine findings

1. Metrics are calculated only from trades with non-null `rMultiple`.
2. `AMBIGUOUS` trades have null `rMultiple` when the same candle touches SL and TP, so they are excluded from closed-trade metrics.
3. `OPEN` trades also have null `rMultiple` and are excluded from closed-trade metrics.
4. The evaluator processes OHLC candles sequentially and resolves SL/TP based on intrabar high/low only; simultaneous SL/TP is explicitly marked `AMBIGUOUS` rather than choosing an ordering.
5. A very small-risk / very high-R 1min trade exists in the baseline report and requires forensic review before any statistical interpretation.

## Geometry contamination findings

The current baseline implementation contains concrete geometry choices that are not fully source-confirmed:

- Entry trigger uses the first post-correction close reclaim and uses the candle close as entry price.
- Invalidation uses the correction extreme as the invalidation level.
- Leg-1 size is implemented as `abs(spikeEnd.close - spikeStart.open)`.
- TP1 is projected from the correction extreme by the implemented Leg-1 size.

The source-resolution matrix explicitly leaves exact Entry anchor, SL OHLC semantics, wick/body semantics, A/B/C/D anchors, AB=CD tolerance, exact trigger taxonomy, and exact TP formulas unresolved.

## Gate status

- Source Resolution: PARTIAL PASS
- Synthetic Fixtures: REQUIRED
- Frozen Geometry: BLOCKED
- Baseline reproduction audit: REQUIRED
- Metric integrity audit: REQUIRED
- Untouched validation: LOCKED
- Robustness/stability: LOCKED
- Fresh holdout: LOCKED
- Production: OFF

## Required next work

1. Reproduce the existing 1min and 5min reports from the recorded dataset and code revision.
2. Enumerate candidate count versus closed/ambiguous/open count.
3. Isolate all tiny-risk and extreme-R trades for forensic inspection.
4. Recompute metrics under an explicitly documented ambiguity policy without changing canonical geometry.
5. Build F8-F15 synthetic fixtures to discriminate only source-supported geometry.
6. Keep any non-discriminated geometry explicitly UNRESOLVED.

## Non-negotiable rule

No baseline metric may be used to choose among unresolved geometry alternatives. No canonical Win Rate, Expectancy, Profit Factor, or production BUY/SELL rule is established by this audit.
