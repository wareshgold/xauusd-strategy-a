# SP2L V3 Balanced Forward Test Profile — RR2 + Trail3 — 2026-10-01

**Status: RESEARCH ONLY / NOT CANONICAL**

## Purpose

Fixed two-day XAUUSD forward test intended to provide a clean, stable execution sample without changing parameters during the test.

## Frozen profile

| Parameter | Value |
|---|---:|
| Symbol | XAUUSD.ecn |
| Timeframe | M1 |
| P-Gap | 1.0 |
| Spike multiplier | 1.5 |
| Max SL | 10.0 |
| Exit target | 2R |
| Trailing | 3 pip |
| XAU pip size | 0.10 price |
| Trailing distance | 0.30 XAU price |
| Volume | 0.01 |
| Order mode | Pending Limit Research |
| Pending TTL | 30 minutes |
| Session | All market hours |
| Live execution | Enabled for this forward-test run |
| Canonical | false |

## Trailing semantics

For BUY, once the favorable move reaches 0.30 price, the trailing SL is calculated as:

`new SL = completed M1 high - 0.30`

For SELL:

`new SL = completed M1 low + 0.30`

The current V3 implementation updates trailing from the latest **completed M1 candle**, not tick-by-tick.

## Test discipline

1. Do not change RR, trailing distance, P-Gap, spike multiplier, SL, or volume during the two-day run.
2. Do not attribute pre-existing MT5 orders, positions, deals, or history to this run.
3. Record actual broker fills/exits and Telegram lifecycle events.
4. After the run, compare MT5 forward results against the corresponding fixed-population research backtest.
5. Trail 3 remains a research candidate; this test does not promote it to canonical Strategy A.

## Historical research reference

The 2026-10-01 V3 exit matrix showed RR2 + Trail3 as a research variant with:
- 1,455 decisive outcomes
- 1,415 wins / 37 losses / 67 ambiguous
- 97.2509% win rate among decisive outcomes
- +585.5864R
- PF 16.82666
- max drawdown 1.65908R

These historical figures are **not treated as proof** of live edge. In particular, trailing/intrabar ordering and the larger ambiguous population require validation.

## Run command

From the repository root:

```powershell
$env:LIVE_TRADING_ENABLE="true"
$env:ALLOW_REAL_EXECUTION="true"
& ".\.venv\Scripts\python.exe" `
  ".\scripts\run_sp2l_v3_xauusd_balanced_forward_test.py"
```

Keep this exact profile unchanged for the test window.
