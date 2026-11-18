# SP2L V3 — 36-position intrabar ambiguity audit

Research-only, offline-only, no P/L, no canonical decisions.

This is an independent diagnostic. It does not edit or import the legacy matrix
runner and does not connect to MetaTrader 5.

## Inputs
- artifacts/v3_matrix/SP2L_V3_ACTUAL_FORWARD_TRAILING_MATRIX_V3_20261005T074420Z_TRADES.csv
- artifacts/v3_matrix/XAUUSD_ECN_M1_20261001_20261006.csv

The tool hard-codes the audited 36-position whitelist, selects only baseline
NO_TRAILING_RR1 rows for those IDs, and rejects missing or duplicate IDs,
unexpected directions, second entries, or multi-entry positions.

## Run
From repository root:

    python scripts/audit_sp2l_v3_matrix_intrabar_ambiguity.py --trades artifacts/v3_matrix/SP2L_V3_ACTUAL_FORWARD_TRAILING_MATRIX_V3_20261005T074420Z_TRADES.csv --m1 artifacts/v3_matrix/XAUUSD_ECN_M1_20261001_20261006.csv --out-dir artifacts/v3_matrix/intrabar_audit_36

Synthetic tests:

    python -m unittest discover -s scripts -p "test_audit_sp2l_v3_matrix_intrabar_ambiguity.py" -v

## Output
For each of 36 trades × 600 legacy parameter combinations = 21,600 audit rows:
- same M1 bar touches both TP and pre-update SL;
- trailing activation/update and updated trailing SL touch occur in one M1 bar;
- 2X level touch, without assuming fill, size change, or weighted entry;
- missing M1 minutes and missing entry/exit minute bars;
- partial entry minutes excluded and partial exit minutes included as whole OHLC bars, both explicitly flagged;
- first possible exit-level-touch bar under the legacy OHLC scan window.

The scan stops at the first possible exit-touch bar because subsequent bars are
not relevant unless it is known the position remained open.

## Limitations
- M1 OHLC cannot reveal the order of high and low inside a candle.
- Entry-minute partial-bar data is not reconstructed; that minute is excluded
  to mirror the legacy replay window.
- Whole exit-minute OHLC is included for diagnostics only. It may include
  post-exit price action and is not proof of an executable exit.
- 2X is level-touch only. No fill semantics are inferred.
- Costs, spread, slippage, commission, swap, latency, and broker constraints
  are not modeled.
- No realized R, USD P/L, win rate, PF, drawdown, ranking, or preferred setup
  is computed.

This audit can locate source insufficiency. It cannot resolve execution
semantics or establish a statistical edge.
