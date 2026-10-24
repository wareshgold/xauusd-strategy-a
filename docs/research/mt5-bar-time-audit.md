# Read-only MT5 bar-time audit

## Purpose

Compare MT5 M1 bar timestamps and OHLC around the reported XAUUSD.ecn gap on 2026-10-20/21. The script checks two explicit query windows:

- Window A: the timestamps as reported (2026-10-20 23:45 through 2026-10-21 01:15)
- Window B: the same interval shifted by three hours (2026-10-21 02:45 through 2026-10-21 04:15)

The second window is a diagnostic comparison only. It is not a proposed correction.

## Safety

- Read-only: calls `SymbolSelect` and `CopyRates` only.
- Does not send, modify, or cancel orders.
- Does not edit source CSVs, manifests, logs, runtime state, or strategy settings.
- Does not apply a timestamp offset or declare any time basis canonical.
- The printed `datetime_value` is an additional comparison field; the script does not assert it is UTC.

## Run in MT5

1. Copy `tools/mt5_audit/SP2L_ReadOnly_BarTimeAudit.mq5` into the terminal data folder's `MQL5\\Scripts\\` directory.
2. Open it in MetaEditor and compile it.
3. In MT5, open the `XAUUSD.ecn` chart and ensure M1 history around 2026-10-20/21 is available.
4. Run `SP2L_ReadOnly_BarTimeAudit` from Navigator > Scripts.
5. Copy the Experts-tab lines from `SP2L READ-ONLY BAR TIME AUDIT` through `AUDIT COMPLETE`.

If a window reports no rates, load the relevant chart history and rerun. Do not edit the input timestamps just to force a match.

## Interpretation guardrail

Compare both timestamp labels and OHLC values with the immutable CSV rows. A timestamp coincidence alone is insufficient: matching OHLC across the candidate windows is the stronger clue. Record the evidence first; do not shift the CSV, rewrite its manifest, or infer a canonical time mapping from this script alone.
