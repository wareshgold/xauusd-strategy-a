# SP2L Live MT5 + Telegram Weekend Build — 2026-09-19

## Objective
Prepare an executable MT5 live-market observer and execution gateway before Monday,
while keeping Strategy A signal generation separate from execution.

## Implemented
- MT5 XAUUSD.ecn live tick observer.
- Explicit signal execution adapter.
- Dry-run by default.
- Duplicate signal_id protection.
- Persistent execution journal/state.
- Optional Telegram echo.
- Standard BUY/SELL signal template.

## Critical boundary
The gateway does NOT calculate SP2L signals. It cannot promote unresolved geometry
into canonical production rules. It accepts an explicitly supplied signal only.

## Signal template
SP2L Strategy A
Signal ID: SP2L-YYYYMMDD-HHMMSS-XXXX
Direction: BUY | SELL
Entry: <price>
SL: <price>
TP: <price>
Volume: <lots>
Status: SIGNAL | DRY_RUN | EXECUTED | REJECTED
MT5: XAUUSD.ecn
Time: <UTC>

## Monday sequence
1. Start MT5 and confirm XAUUSD.ecn.
2. Run gateway in DRY-RUN.
3. Verify market heartbeat and Telegram.
4. Test a known signal payload and verify DRY_RUN + Telegram.
5. Repeat the same signal_id and verify DUPLICATE_REJECTED.
6. Only with explicit human authorization, enable live execution and use a test-sized order.
7. Reconcile MT5 order/deal, gateway journal and Telegram.
8. Keep Fresh Holdout frozen and separate.

Production Strategy A authorization remains blocked pending the frozen Fresh Holdout
and remaining validation gates.
