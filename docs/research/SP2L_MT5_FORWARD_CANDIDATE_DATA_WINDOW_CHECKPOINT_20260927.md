# SP2L MT5 Forward Candidate Data Window Checkpoint — 2026-09-27

## Finding
The requested 2026-01-01 to 2026-09-25 MT5 local multi-symbol backtest cannot be completed because the connected terminal does not expose M1 history back to 2026-01-01.

Observed first trading dates:
- XAUUSD.ecn: 2026-06-17
- USDJPY.ecn: 2026-06-22
- EURJPY.ecn: 2026-06-22
- GBPUSD.ecn: 2026-06-22
- GBPJPY.ecn: 2026-06-22
- EURUSD.ecn: 2026-06-22
- USDCHF.ecn: 2026-06-22
- USDCAD.ecn: 2026-06-22

## Implication
The common data-supported window for the full 8-symbol universe begins 2026-06-22. The failed 2026-01-01 request produced INCOMPLETE_HISTORY and zero trades; it is not a performance result.

## Research policy
Do not backfill or silently normalize missing history. A common-window baseline may be run from 2026-06-22 through 2026-09-25 for cross-symbol comparability, while the requested January-start matrix remains data-incomplete.

research_only=true
canonical=false
