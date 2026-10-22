# Strategy B Forward Observer Runbook — 2026-10-22

## Status

Research-only, read-only observer. It is not an execution replica and is not approved for live/demo orders. No statistical edge is established.

Source audit: [STRATEGY_B_PYTHONTRADERBOT_SOURCE_AUDIT_20261022.md](STRATEGY_B_PYTHONTRADERBOT_SOURCE_AUDIT_20261022.md)

## Isolation contract

- Dedicated branch: `research/strategy-b-pythontraderbot-forward-20261022`.
- Observer entry point: `scripts/run_strategy_b_forward_observer.py`.
- Core: `scripts/strategy_b_pythontraderbot_core.py`.
- Events: `artifacts/strategy-b-forward/STRATEGY_B_FORWARD_EVENTS.jsonl`.
- State: `runtime/strategy_b_forward_observer_state.json`.
- Lock: `runtime/strategy_b_forward_observer.lock`.
- Source strategy default remains `XAUUSD`; the broker adapter defaults to the operator-verified available symbol `XAUUSD.ecn` and records `EXPLICIT_BROKER_SUFFIX_ADAPTER` in identity/events. This is an explicit environment mapping, not a claim that the broker symbol name is identical to source. Arbitrary symbol names are rejected.
- No order placement/modification/cancellation APIs are present in the observer.
- Startup is blocked unless `STRATEGY_B_OBSERVER_ENABLE=true`.
- State is cleared if the detected server/account metadata or symbol specification changes. State schema/strategy mismatch fails closed.
- A stale lock is deliberately not auto-deleted. Inspect its PID and confirm the process is absent before removing the lock manually.

Strategy A files, event logs, state, process, magic number, and configuration are not used or modified by this observer.

## MT5 attachment safety gate

Before an observer start, set `STRATEGY_B_MT5_TERMINAL_PATH` to the full executable path of the already-running terminal (for this machine, `C:\Program Files\Otet Group MT5 Terminal\terminal64.exe`). The observer checks through Windows process metadata that this exact executable is already running before creating observer files, calls `mt5.initialize(path=..., timeout=10000)` rather than bare initialization, and verifies the connected terminal directory matches the configured executable directory. If the process cannot be verified or the path differs, it fails closed. It does not launch MT5 intentionally.

The preflight on 2026-10-22 confirmed PID 8940 at that exact path, server `OtetGroup-MT5`, symbol `XAUUSD.ecn`, point `0.01`, zero open orders and zero positions at the time of inspection. This is a snapshot, not a persistent guarantee; repeat preflight immediately before any observer start. The observer remains opt-in and has not been started by this change.

## Source-derived defaults

- M1; 500 bars available to the observer (source live bot's lookback); polling interval defaults to 0.5 seconds, matching the source live bot.
- Spike body multiplier 1.5.
- P-Gap 100 broker points, converted using the connected broker symbol's actual `point` (current preflight: `0.01`, so P-Gap price distance is `1.00`).
- Maximum stop distance 1000 broker points, converted using the connected broker symbol's actual `point` (current preflight: `10.00` price units).
- TP 0.9R.
- Pivot SL disabled; default SL is the candle before the spike (BUY low / SELL high).
- EMA close-vs-EMA filter enabled, period 60.
- Trend-structure filter enabled, maximum opposite moves 1.
- Range, ADX-rising, session filters disabled.
- Second entry disabled / not implemented.
- Source live bot uses 0.01 lot, but the observer never sizes or submits an order.

## Important limitations

1. This observer records setup and entry candidates only. It does not reproduce broker execution, fill-based TP recalculation, order lifecycle, trade outcomes, or Telegram behavior.
2. Candle geometry and enabled filters still require line-by-line differential fixtures against the exact pinned source and notebook, especially EMA initialization, trend-filter interpretation, pivot SL, and timestamp handling.
3. The current implementation evaluates current/forming M1 candles and therefore can record intrabar observations that later change. Events are immutable observations, not confirmed closed-bar signals.
4. Event candidates are not trades. Do not calculate win rate/PF/expectancy from candidate events without broker-confirmed fills and reconciled exits.
5. This is not a statistically validated strategy and must not autonomously generate production BUY/SELL decisions.
6. Do not add order execution to this script. Any future demo execution adapter must be a separate reviewed change with explicit account, symbol, volume, magic-number, existing-order/position, and broker constraint preflight.

## Local offline validation

Run only the synthetic tests first:

```powershell
$Repo = "D:\Mirzaei\Private\1\xauusd-strategy-b-pythontraderbot-20261022"
$Python = (Get-Command python -ErrorAction Stop).Source
Push-Location $Repo
try {
    & $Python -m py_compile scripts\strategy_b_pythontraderbot_core.py scripts\run_strategy_b_forward_observer.py tests\test_strategy_b_pythontraderbot_core.py tests\test_strategy_b_forward_observer_safety.py
    if ($LASTEXITCODE -ne 0) { throw "Compile failed" }
    & $Python -m pytest -q tests\test_strategy_b_pythontraderbot_core.py tests\test_strategy_b_forward_observer_safety.py
    if ($LASTEXITCODE -ne 0) { throw "Strategy B offline tests failed" }
}
finally { Pop-Location }
```

Only after tests pass and a separate read-only terminal/account preflight is reviewed should the observer be considered for a bounded, supervised run. The current operator preflight confirmed the `OtetGroup-MT5` session and `XAUUSD.ecn` point/digits. Before starting, run the full read-only symbol/account/order/position preflight and inspect source magic values 8/9; this observer itself never submits or modifies orders. Starting the observer remains a separate, explicit operator action.


## Source-parity refinement (2026-10-22)

- EMA is enabled in the source live bot. The observer now mirrors its initialization/update pattern: initial EWM with `adjust=False` over fetched history, then updates only the forming candle from the previous candle's cached EMA on each poll. It does not recompute the EMA across the rolling window every 0.5 seconds.
- The observer no longer calls `mt5.symbol_select`; the operator's read-only preflight showed `XAUUSD.ecn` is already visible, so Market Watch selection need not be changed.
- These are research-observation parity improvements, not execution parity. The observer still cannot submit or modify orders and must pass local tests before an operator starts it.
