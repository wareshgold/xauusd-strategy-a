# Offline 36-position replay — design and limits

## Purpose
A reproducible, offline, research-only sensitivity analysis for the exact 36-position population reconciled to the original RR2/TRAIL4 Runner. It does not resolve canonical SP2L source rules.

## Inputs and population
- Trade fixture: artifacts/v3_matrix/SP2L_V3_ACTUAL_FORWARD_TRAILING_MATRIX_V3_20261005T074420Z_TRADES.csv
- M1 fixture: artifacts/v3_matrix/XAUUSD_ECN_M1_20261001_20261006.csv
- Only NO_TRAILING_RR1 rows supply entry and SL fields.
- Exact 36-position whitelist; expected direction split 18 BUY / 18 SELL.
- Known extras 62417157 and 62429827 are excluded.
- entry2_filled must be false and total_entries must be one.

## Method
- No MetaTrader5 dependency or connection.
- Entire entry minute is excluded because fill time within that OHLC bar is unknown.
- Observed exit time, exit price and observed P/L do not cap or score the counterfactual replay.
- Replay continues over available M1 bars until a theoretical trigger, a data gap, or end of file.
- Two OHLC-consistent path orderings are evaluated: open → adverse extreme → favorable extreme → close; and open → favorable extreme → adverse extreme → close.
- Divergent outcomes are recorded as path ambiguity. These are sensitivity cases, not probabilities or exhaustive tick paths.
- Original RR / activation / trail grids are retained. 2X is excluded because its semantics and intrabar ordering remain unresolved.
- 300 variants × 2 path cases × 36 positions.

## Explicit limitations
1. OHLC does not reveal the true tick sequence. Two paths do not bound every possible path.
2. Stop/TP trigger prices are theoretical touch-price proxies, not broker fills. Opening gaps through a trigger are unresolved.
3. Commission, swap, slippage, spread execution and broker stop-distance constraints are omitted. USD is a gross proxy using the legacy assumption contract size 100 and volume 0.01; R is the primary normalized output.
4. A data gap censors a still-open position; no price path or fill is invented across missing minutes.
5. Entry and SL come from NO_TRAILING_RR1 weighted_entry / final_sl. Their equivalence to the exact original initial-order values still needs forensic order-record confirmation.
6. M1 ends on 2026-10-05. Positions still open are END_OF_DATA, not force-closed.
7. The 36 trades are a selected historical sample, not an untouched holdout. No ranking, optimization or edge claim is authorized.

## Run
PowerShell:
python scripts/research_replay_36_path_bounds.py --trades artifacts/v3_matrix/SP2L_V3_ACTUAL_FORWARD_TRAILING_MATRIX_V3_20261005T074420Z_TRADES.csv --m1 artifacts/v3_matrix/XAUUSD_ECN_M1_20261001_20261006.csv --out artifacts/v3_matrix/offline_36_path_bounds

Synthetic tests:
python -m unittest tests.test_offline_36_path_bounds -v

Outputs: trade_results.csv, scenario_summary.csv, path_ambiguities.csv, manifest.json.
All outputs are research-only, noncanonical, and must not be used for production BUY/SELL decisions.
