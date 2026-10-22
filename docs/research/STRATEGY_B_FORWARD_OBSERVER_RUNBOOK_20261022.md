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
- Exact source symbol only: `XAUUSD`; no automatic substitution to `XAUUSD.ecn`.
- No order placement/modification/cancellation APIs are present in the observer.
- Startup is blocked unless `STRATEGY_B_OBSERVER_ENABLE=true`.
- State is cleared if the detected server/account metadata or symbol specification changes. State schema/strategy mismatch fails closed.
- A stale lock is deliberately not auto-deleted. Inspect its PID and confirm the process is absent before removing the lock manually.

Strategy A files, event logs, state, process, magic number, and configuration are not used or modified by this observer.

## Source-derived defaults

- M1; 500 bars available to the observer (source live bot's lookback).
- Spike body multiplier 1.5.
- P-Gap 100 broker points, converted using the connected symbol's actual `point`.
- Maximum stop distance 1000 broker points.
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

Only after tests pass and a separate read-only terminal/account preflight is reviewed should the observer be considered for a bounded, supervised run. No startup command is provided here because the account/session and symbol point have not yet been verified.
