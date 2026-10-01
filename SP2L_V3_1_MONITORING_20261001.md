# SP2L V3.1 Monitoring — 2026-10-01

## Purpose
V3.1 adds a dedicated read-only localhost dashboard for the XAUUSD RR2/Trail3 forward test. It does not change strategy geometry, execution, trailing semantics, or canonical status.

## Fixed research profile
- Symbol: XAUUSD.ecn
- P-Gap: 1.0
- Spike multiplier: 1.5
- Max SL: 10.0
- RR: 2.0
- Trail: 3 V3 pips = 0.30 XAU price
- Volume: 0.01
- Pending Limit, TTL 30 minutes
- canonical=false / research-only

## Data boundary
The monitor reads:
- `runtime/sp2l_v3_xauusd_rr2_trail3_forward_state.json`
- `artifacts/forward-test/SP2L_V3_XAUUSD_RR2_TRAIL3_FORWARD_EVENTS.jsonl`
- MT5 account/tick/orders/positions through read-only APIs.

It never calls `order_send`, never modifies state, and never sends Telegram messages.

## Run
Start the existing V3.1 forward test first. In a second PowerShell:

```powershell
cd "D:\Mirzaei\Private\1\xauusd-strategy-a"
& ".\.venv\Scripts\python.exe" ".\scripts\sp2l_v31_monitor.py"
```

Open `http://127.0.0.1:8790`.

The dashboard auto-refreshes every 3 seconds. `/api/status` exposes the same read-only status as JSON.
