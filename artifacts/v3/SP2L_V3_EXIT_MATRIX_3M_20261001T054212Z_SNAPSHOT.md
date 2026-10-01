# SP2L V3 Exit Matrix Snapshot

Version: SP2L_V3_TRAIL_SENSITIVITY_20261001
Window UTC: 2026-07-01T00:00:00+00:00 → 2026-10-01T00:00:00+00:00
Symbol: XAUUSD.ecn
Timeframe: M1
Bars: 90637

Frozen signal population: 1522 signals
All exit variants replay exactly this same population.

Geometry:
- pGap=1.0
- spikeMultiplier=1.5
- maxSL=10.0
- entry policy=sp2l_v3_config.find_first_entry
- session=ALL_MARKET_HOURS

Volume: 0.01
Contract size: 100.0
USD per 1.00 XAU price movement at 0.01 lot: 1.0000
Spread/slippage/commission: not modeled

Variants:
- RR1_NO_TRAIL
- RR2_NO_TRAIL
- RR1_TRAIL5
- RR1_TRAIL10
- RR1_TRAIL15
- RR1_TRAIL20
- RR1_TRAIL30
- RR2_TRAIL5
- RR2_TRAIL10
- RR2_TRAIL15
- RR2_TRAIL20
- RR2_TRAIL30

Trailing: completed M1 bar high/low.
Same-bar SL + TP: ambiguous and excluded from decisive win rate.
Trailing is research-only and not source-confirmed canonical Strategy A.

JSON SHA256: 19f8f26d0cdf72d8374d8357f209aaae74adff1bd0fc5d83e8106592178152e0
