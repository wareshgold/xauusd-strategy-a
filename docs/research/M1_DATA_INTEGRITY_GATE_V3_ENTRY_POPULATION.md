# M1 Data Integrity Gate — V3 Entry Population

Status: research infrastructure proposal, not canonical Strategy A geometry.

## Purpose

The first Factory stage uses the existing SP2L V3 output as its declared
signal/entry population. It does not redefine, optimize, filter, or recompute
those entries. The exact preserved M1 source and V3 trade CSV are both bound
by their recorded SHA-256 before the controlled exit matrix runs.

The currently identified inputs are:

- M1 CSV: `xauusd_ecn_m1_30d.csv`, 29,919 bars, coverage
  `2026-09-24T07:57:00Z` through `2026-10-23T23:57:00Z`,
  SHA-256 `B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285`.
- Frozen V3 Strategy A entry CSV: `a_trail_0_40_activated_proxy_v3_trades.csv`,
  462 rows, SHA-256
  `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`.

## Enforced checks

- UTF-8 JSON or the exact preserved MT5 M1 CSV schema.
- Explicit `research_only=true`, expected symbol, and M1 timeframe.
- Exact artifact window match against the declared HistoricalTestSpec window.
- Existing M1 CSV bytes are reused directly; no fresh MT5 re-export is required.
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

- The frozen V3 entry CSV is the sole signal/entry population for every exit variant.
- The loader uses direction, setup/entry timestamps, entry proxy, initial SL, and risk.
- Previous V3 target/exit time/exit price/exit reason/status/R multiple are ignored.
- Every frozen entry timestamp must match exactly one M1 bar. Trade identity is
  `(entry_time_utc, direction, entry_proxy, sl_initial)`; an exact duplicate
  trade identity, wrong order, wrong SHA, or missing M1 timestamp fails closed.
- The frozen artifact contains 462 rows and 462 unique trade identities, but
  452 signal identities `(entry_time_utc, direction, entry_proxy)`. Ten signal
  groups contain two distinct initial-stop definitions each. All rows are
  preserved. This identity rule does not assert that same-signal trades are
  independently executable in a live account.
- The existing V3 configuration remains the source of its research geometry.
- This does not resolve source meaning for canonical SP2L, P-Gap, AB=CD anchors,
  fill semantics, or production execution rules.
- The existing Discovery Matrix remains M1 OHLC research; spread, slippage,
  and commission are still not modeled there.
- No parameter winner, statistical edge, untouched-validation result,
  Fresh Holdout result, or production authorization is created by this gate.
- No MT5 export or Discovery run is triggered automatically by this code change.
- The V3 trade CSV is an entry-population artifact, not evidence that its prior
  exit outcomes remain valid under the new exit matrix.

## Required next evidence

1. Run the focused integrity and Discovery adapter/factory tests.
2. Run the full repository test suite.
3. Only then, manually authorize a DEVELOPMENT dataset export and controlled
   V3 exit-discovery run using the fixed V3 entry population.
4. Preserve the resulting dataset, integrity report, Discovery JSON/CSVs,
   and hashes as immutable evidence.
