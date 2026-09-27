# SP2L MT5 Common Window Gate Checkpoint — 2026-09-27

## Result
The attempted common-window backtest `2026-06-22T00:00:00Z` to `2026-09-25T23:59:59Z` remains INCOMPLETE_HISTORY for the 8-symbol universe.

XAUUSD.ecn completed: 58,810 M1 bars; 650 signals; 357 decisive; 96 wins; 261 losses; WR 26.890756%; net -165R; PF simplified 0.367816; max DD 167R; max loss streak 12.

The seven FX symbols were rejected because their first observed bar on 2026-06-22 occurred substantially after 00:00 UTC and did not match the runner's recurring daily opening-edge expectation:
USDJPY 11:54, EURJPY 11:00, GBPUSD 11:09, GBPJPY 12:20, EURUSD 12:04, USDCHF 11:22, USDCAD 10:53 UTC.

## Interpretation
The combined 8-symbol result must NOT be treated as a comparable 8-symbol baseline because seven symbols failed the history gate. XAUUSD's completed result is a valid descriptive output for this run, but is not sufficient to select forward candidates.

The next research action is to resolve whether the FX late first bars are an artifact of the runner's daily opening-edge completeness check or a genuine data-window limitation. No data deletion, gap filling, or canonical rule change is authorized by this checkpoint.

research_only=true
canonical=false
