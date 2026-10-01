# SP2L V3 — Official Research Snapshot

**Version:** SP2L_V3_XAUUSD_TRAIL10_20261001
**Branch:** research/sp2l-strategy-a-v3-trailing10-20261001
**Snapshot commit:** 7fb33189e3ef76da746218f9115ca55482bc3a08
**Scope:** XAUUSD.ecn / M1 / 3-month MT5 research
**Status:** RESEARCH VARIANT — NOT CANONICAL

## Frozen configuration
- P-Gap price threshold: 1.0
- Spike body multiplier: 1.5
- Maximum SL distance: 10.0 price units
- Initial TP: 1.0R
- Pending order: BUY_LIMIT / SELL_LIMIT research mode
- SL anchor: spike-start candle extreme (research implementation)
- Pending TTL: 30 minutes
- Session policy: ALL_MARKET_HOURS
- Volume: 0.01
- Trailing stop: 10 pips
- XAUUSD pip size: 0.10 price units
- Trail 10 = 1.00 price unit
- TP remains fixed at initial 1R

## Trailing semantics
Trailing is a research execution variant. It activates after favorable movement reaches 10 pips. The stop is monotonic. Historical Python simulation uses completed M1 bar high/low extremes. A completed M1 bar touching both active SL and fixed TP is AMBIGUOUS.

## Artifacts in this V3 branch
- scripts/sp2l_v3_config.py
- scripts/run_sp2l_v3_xauusd_backtest.py
- scripts/run_sp2l_v3_xauusd_forward_test.py
- MQL5/Experts/SP2L_V3_XAUUSD_TRAIL10.mq5
- docs/research/SP2L_V3_RUNBOOK_20261001.md
- this official snapshot

## Reproducibility contract
Every Python 3-month run writes JSON trade journal, CSV trade journal, SHA-256, and run snapshot. Forward writes a V3-isolated JSONL event stream with candidate/order/broker lifecycle/trailing events. MT5 Strategy Tester writes its own CSV journal.

## Source boundary
Trail 10 is NOT promoted to canonical Strategy A. The exact trailing execution semantics are a research variant. Backtest performance cannot promote it.

## Required first historical window
2026-07-01T00:00:00Z through 2026-10-01T00:00:00Z.

The actual MT5 bar count, symbol specification, and data availability must be preserved in generated outputs. No missing-data interpolation is permitted.
