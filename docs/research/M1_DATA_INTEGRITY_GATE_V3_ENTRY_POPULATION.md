# M1 Data Integrity Gate — V3 Entry Population

Status: research infrastructure proposal, not canonical Strategy A geometry.

## Purpose

The first Factory stage continues to use the existing SP2L V3 output as its
declared signal/entry population. This gate does not redefine, optimize, or
filter those entries. It validates the exact M1 artifact before the existing
V3 controlled Discovery Matrix is allowed to consume it.

## Enforced checks

- UTF-8 JSON and supported artifact schema.
- Explicit `research_only=true`, expected symbol, and M1 timeframe.
- Exact artifact window match against the declared HistoricalTestSpec window.
- Inclusive `[start, end]` timestamp bounds, matching the MT5
  `copy_rates_range` date range convention used by the exporter.
- Integer Unix timestamps aligned to M1 boundaries.
- Strictly increasing timestamps; duplicates and out-of-order bars are rejected.
  No sorting, deduplication, interpolation, or repair is performed by this gate.
- Finite, positive OHLC values with internally consistent high/low.
- Non-negative integer tick_volume, spread, and real_volume.
- Exact raw-byte SHA-256 and byte-size binding.
- Re-hash after Discovery completes to detect mutation during the run.

## Gap semantics

Missing-minute intervals are counted and reported as `PASS_WITH_GAPS`.
They are not filled, silently discarded, or automatically classified as market
closures versus missing market data. No session calendar or gap threshold is
invented here. A later analysis must inspect the reported gaps against the
source's actual trading schedule before interpreting performance.

## Scope boundaries

- V3 signal and entry population remains fixed for all exit-management variants.
- The existing V3 configuration remains the source of its research geometry.
- This does not resolve source meaning for canonical SP2L, P-Gap, AB=CD anchors,
  fill semantics, or production execution rules.
- The existing Discovery Matrix remains M1 OHLC research; spread, slippage,
  and commission are still not modeled there.
- No parameter winner, statistical edge, untouched-validation result,
  Fresh Holdout result, or production authorization is created by this gate.
- No MT5 export or Discovery run is triggered automatically by this code change.

## Required next evidence

1. Run the focused integrity and Discovery adapter/factory tests.
2. Run the full repository test suite.
3. Only then, manually authorize a DEVELOPMENT dataset export and controlled
   V3 exit-discovery run using the fixed V3 entry population.
4. Preserve the resulting dataset, integrity report, Discovery JSON/CSVs,
   and hashes as immutable evidence.
