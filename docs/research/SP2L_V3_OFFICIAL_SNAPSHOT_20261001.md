# SP2L V3 — Official Research Snapshot

**Version:** SP2L_V3_XAUUSD_TRAIL10_20261001  
**Branch:** research/sp2l-strategy-a-v3-trailing10-20261001  
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
- Therefore Trail 10 = 1.00 price unit
- TP remains fixed at the initial 1R level

## Trailing semantics
Trailing is a research execution variant. It is activated only after favorable movement reaches 10 pips. The stop is monotonic: it may move only in the profitable direction. The V3 historical simulation uses completed M1 bar high/low extremes. If the same completed M1 bar touches both the active SL and fixed TP, the trade is marked **AMBIGUOUS** rather than assigning an outcome.

## Reproducibility contract
Every 3-month run writes:
1. JSON trade journal with every signal and exit field.
2. CSV trade journal.
3. SHA-256 hash of the JSON result.
4. Run snapshot containing the exact configuration and data window.
5. Forward JSONL event stream containing candidate, order, broker lifecycle, and TRAIL_UPDATE events.

## Important source boundary
Trail 10 is not promoted to a canonical Strategy A rule by this snapshot. It is an explicitly named research variant because source evidence does not establish the exact trailing execution semantics.

## Required 3-month window
Default: **2026-07-01T00:00:00Z through 2026-10-01T00:00:00Z**.

The MT5 broker's actual available bars, symbol specification, and returned bar count must be preserved in the generated snapshot. No missing-data interpolation is permitted.
