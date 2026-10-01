# SP2L V3 Exit Matrix (costed) Snapshot

Version: SP2L_V3_EXIT_MATRIX_COSTED_20261001
Window UTC: 2026-07-01T00:00:00+00:00 → 2026-10-01T00:00:00+00:00
Symbol: XAUUSD.ecn
Timeframe: M1
Bars: 90637

Frozen signal population: 1522 signals (identical to uncased matrix).

Costs modeled:
- spread: 0.2 price units, full amount once per trade (BUY pays at entry, SELL at exit)
- slippage: 0.05 price units on stop-type exits only (SL / TRAIL_SL); TP fills exact
- calibration: live spread observed 0.18, live SL slippage observed 0.06 worst

Walk-forward split (signal_time_utc frame): TRAIN < 2026-09-01T00:00:00+00:00 <= VALIDATE
- TRAIN = July + August 2026, VALIDATE = September 2026

Trailing: completed M1 bar high/low; same-bar SL+TP ambiguous and excluded.
Volume: 0.01, contract size: 100.0.

JSON SHA256: e60c989a3241ec9eaed00b0f310cc6111663862181e3505f742158c75ba4718c
