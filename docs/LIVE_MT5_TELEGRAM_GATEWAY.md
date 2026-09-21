# Live MT5 + Telegram Gateway (research branch)

## Purpose

This branch adds an execution/notification shell for the existing MT5 integration.

It is **not** a canonical Strategy A signal engine.

The gateway:
- connects to the local MetaTrader 5 terminal;
- reads live XAUUSD.ecn bid/ask/account state;
- accepts a JSON signal only when `status=APPROVED`;
- validates symbol and direction;
- supports MT5 market execution with SL/TP;
- sends the signal and execution result to Telegram;
- archives consumed signal files;
- defaults to dry-run.

## Current safety boundary

`LIVE_TRADING_ENABLE=false` is the default.

The gateway does not infer P-Gap, AB=CD, Leg 1/Leg 2, fill semantics, or any other unresolved Strategy A geometry.

The existing author-replica scripts remain research-only and must not be silently promoted into the live signal source.

## Monday target

The first Monday deployment target should be:

1. MT5 terminal connected to the intended account.
2. Gateway starts and reports connection/account status.
3. Live bid/ask heartbeat is visible.
4. Telegram test message arrives.
5. A manually supplied APPROVED test signal reaches the gateway.
6. With LIVE disabled, the gateway produces the exact MT5 request but sends no order.
7. Only after explicit human verification should live execution be enabled.
8. Strategy-generated signals remain blocked until Frozen Geometry is resolved and the canonical validation gates are passed.

## Signal contract

Example:

```json
{
  "direction": "BUY",
  "symbol": "XAUUSD.ecn",
  "entry": 0.0,
  "sl": 0.0,
  "tp": 0.0,
  "volume": 0.01,
  "signal_id": "SIG-YYYYMMDD-HHMMSS-001",
  "source": "HUMAN_APPROVED_OR_CANONICAL_ENGINE",
  "status": "APPROVED"
}
```

SELL uses the same schema with `direction: SELL`.

## Telegram template

### BUY

🟢 SP2L — BUY

Symbol: XAUUSD.ecn
Entry: <ENTRY>
SL: <SL>
TP: <TP>
Volume: <VOLUME>
Signal ID: <SIGNAL_ID>
Source: <SOURCE>
Mode: DRY-RUN / LIVE

### SELL

🔴 SP2L — SELL

Symbol: XAUUSD.ecn
Entry: <ENTRY>
SL: <SL>
TP: <TP>
Volume: <VOLUME>
Signal ID: <SIGNAL_ID>
Source: <SOURCE>
Mode: DRY-RUN / LIVE

### Execution acknowledgement

MT5 retcode: <RETCODE>
Order: <ORDER>
Deal: <DEAL>
Comment: <COMMENT>

## Local setup

Install the Python MetaTrader 5 package in the same Python environment that already reaches the local MT5 terminal.

Set the environment variables from `runtime/live-trader.env.example`.

Never commit:
- Telegram bot token;
- Telegram chat ID if treated as secret in the deployment environment;
- broker credentials;
- local runtime signal files.

## Start in dry-run

```powershell
python scripts/live_mt5_gateway.py
```

The process should report the terminal/server/connection state and send a Telegram startup message.

To test the execution path, place a manually approved JSON payload at:

```
runtime/approved_signal.json
```

The gateway will validate it, print the resulting MT5 request, send the signal/execution status to Telegram, and archive the consumed file.

## Enabling live execution

Only after the dry-run path is verified end-to-end:

```
LIVE_TRADING_ENABLE=true
```

Then restart the gateway.

This switch is intentionally explicit because the project is not yet at the production Strategy A gate.

## Required Monday checks

- [ ] Correct MT5 terminal
- [ ] Correct account/server
- [ ] Correct symbol
- [ ] Trade permission confirmed
- [ ] Correct volume/contract specification
- [ ] SL/TP accepted by broker
- [ ] Telegram delivery confirmed
- [ ] Duplicate-signal protection tested
- [ ] Maximum-open-position guard tested
- [ ] Gateway restart behavior tested
- [ ] Dry-run tested before any live order
- [ ] Canonical Strategy A signal source still blocked unless its validation gate is actually passed

## One-command session (pre-flight + gateway)

The pre-flight checker inspects MT5 terminal/account/symbol state, Telegram
configuration, and the real-execution double gate. It only inspects — it
never changes configuration and never enables trading.

```powershell
# Pre-flight only (exit 0 = READY, 1 = NOT_READY/PARTIAL):
python scripts/run_live_session.py --check-only

# Dry-run session (default; every execution is journal-only, no order):
python scripts/run_live_session.py

# REAL orders: requires ALL of the following or the runner refuses to start:
#   --mode real  AND  LIVE_TRADING_ENABLE=true  AND  ALLOW_REAL_EXECUTION=true
#   AND pre-flight verdict READY
python scripts/run_live_session.py --mode real
```

Real-execution double gate (defense in depth):

| `LIVE_TRADING_ENABLE` | `ALLOW_REAL_EXECUTION` | Result |
|---|---|---|
| false | any | dry-run (order request journal-only) |
| true | false/absent | dry-run (reason: `ALLOW_REAL_EXECUTION!=true`) |
| true | true | real `order_send` to MT5 |

The Telegram message mode label reflects this truthfully: it shows `LIVE`
only when both keys are set.

### Readiness verdicts

- `READY` — every probed component verified; real mode may start.
- `PARTIAL` — nothing failed but some component was not verified (e.g. MT5
  probe skipped); real mode is refused.
- `NOT_READY` — at least one FAILED item (terminal, account permission, or
  symbol trade mode); real mode is refused.

Telegram unconfigured is `DEGRADED` (alerts missing) and never blocks
execution — the trading path is independent of the alerting path.

Note: `symbol_trade_mode` for this broker's `XAUUSD.ecn` was observed as
`CLOSEONLY` on 2026-09-21. Opening new positions on it will be rejected by
the terminal; the pre-flight check surfaces this so the operator can confirm
the intended symbol/account before going live.
