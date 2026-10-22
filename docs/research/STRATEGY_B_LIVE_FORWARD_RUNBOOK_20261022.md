# Strategy B PythonTraderBot demo forward test — 2026-10-22

## Scope
This is an isolated copy of the upstream live bot at
`AlirezaSadabadi/PythonTraderBot/code/SP2L/SP2L_Advanced_Bot_Optimized.py`
(commit/blob reviewed 2026-10-22: `14c936ed1810e8101a4ead74f3536ae6f3a6e4f5`), with the broker symbol adapter and safety/identity changes documented here. The source strategy values are not optimized.

## Preserved live-source settings
- M1, 500 candles, 0.5-second loop, spike body multiplier 1.5
- P-Gap 100 broker points; max SL distance 1000 broker points
- TP = 0.9R; SL from the candle immediately before the spike
- EMA60 filter on; trend filter on; maximum opposite moves 1
- range/ADX, ADX rising, New York session filters off
- second entry off; lot 0.01; magic 8 (second-entry magic 9 remains inactive)
- source's market-order execution and actual-fill TP recalculation retained

## Broker adapter and guardrails
- Source symbol is `XAUUSD`; this account's visible symbol is `XAUUSD.ecn`. Runner defaults to `XAUUSD.ecn` and does not auto-select symbols.
- Explicit absolute terminal executable is mandatory; runner checks that exact `terminal64.exe` is already running, initializes using that path, then verifies the connected terminal directory.
- Only server `OtetGroup-MT5` and MT5 demo-account mode are permitted. Real-account execution is blocked.
- Both `STRATEGY_B_LIVE_TRADING_ENABLE=true` and `STRATEGY_B_ALLOW_DEMO_EXECUTION=true` are mandatory.
- MT5 order comment: `Strategy B PythonTraderBot`; magic 8 identifies the first-entry strategy.
- Telegram credentials are environment variables only; every message from this copy is prefixed `STRATEGY B |`. No Strategy A configuration/state is read or modified.
- Source logic still uses the forming M1 candle and the upstream 0.5-second loop. This remains an experimental demo forward test, not validated production authority.

## Windows launch environment
Set these in the same PowerShell session before running the script:
- `$env:STRATEGY_B_LIVE_TRADING_ENABLE = "true"`
- `$env:STRATEGY_B_ALLOW_DEMO_EXECUTION = "true"`
- `$env:STRATEGY_B_MT5_TERMINAL_PATH = "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe"`
- `$env:STRATEGY_B_EXPECTED_SERVER = "OtetGroup-MT5"`
- `$env:STRATEGY_B_SYMBOL = "XAUUSD.ecn"`
- `$env:STRATEGY_B_TELEGRAM_BOT_TOKEN` and `$env:STRATEGY_B_TELEGRAM_CHAT_ID` must be supplied privately; never commit them.
- If the user's local Telegram proxy is required, set `$env:STRATEGY_B_TELEGRAM_PROXY = "http://127.0.0.1:1090"`; otherwise leave it unset.

Run from the repository root with the project's Python environment:
`python scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py`

## Operational warning
This script sends market orders to the configured MT5 demo account when its source strategy triggers. It is not read-only. Keep Strategy A running independently. Before starting, verify the expected account/server, no pre-existing Strategy B magic-8 position/order, Telegram credentials, dependencies, and that Strategy A's runner/state/logs remain untouched. This source bot does not implement a persistent restart ledger; don't run two Strategy B copies concurrently.
