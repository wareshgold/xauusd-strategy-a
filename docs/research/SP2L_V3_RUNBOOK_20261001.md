# SP2L V3 Runbook — 2026-10-01

Branch: research/sp2l-strategy-a-v3-trailing10-20261001
Version: SP2L_V3_XAUUSD_TRAIL10_20261001

## 1. Pull the exact V3 branch
PowerShell:
git fetch origin
git checkout research/sp2l-strategy-a-v3-trailing10-20261001
git pull --ff-only

## 2. Python/MT5 three-month historical backtest
Default window: 2026-07-01 through 2026-10-01 UTC.
& ".\.venv\Scripts\python.exe" `
  ".\scripts\run_sp2l_v3_xauusd_backtest.py" `
  --mt5-path "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe" `
  --symbol "XAUUSD.ecn" `
  --start "2026-07-01T00:00:00+00:00" `
  --end "2026-10-01T00:00:00+00:00"

Writes JSON trade journal, CSV trade journal, SHA-256 and run snapshot under artifacts/v3/.

## 3. V3 Demo forward test
First ensure no other SP2L forward runner is active, then:
$env:LIVE_TRADING_ENABLE="true"
$env:ALLOW_REAL_EXECUTION="true"
& ".\.venv\Scripts\python.exe" `
  ".\scripts\run_sp2l_v3_xauusd_forward_test.py"

Forward events: artifacts/forward-test/SP2L_V3_XAUUSD_TRAIL10_FORWARD_EVENTS.jsonl
Forward state: runtime/sp2l_v3_xauusd_trail10_forward_state.json
A real Demo order is confirmed only by ORDER_RESULT with dry_run:false plus a broker ticket and MT5 lifecycle evidence.

## 4. MT5 Strategy Tester
Expert file: MQL5/Experts/SP2L_V3_XAUUSD_TRAIL10.mq5
Tester: XAUUSD.ecn / M1 / Every tick based on real ticks when available / 2026.07.01 through 2026.09.30.
Keep volume 0.01 and all V3 inputs unchanged for the first comparison.
EA journal: SP2L_V3_XAUUSD_TRAIL10_MT5_JOURNAL.csv

## 5. Comparison rule
Record bar count/data window, signals, decisive, wins/losses/ambiguous, decisive win rate, net R, profit factor, maximum drawdown, every signal's timestamp/direction/entry/SL/TP, every trailing activation/update, final SL, exit reason, broker retcodes, and hashes.

The Python model uses completed-M1-bar high/low trailing and marks TP+SL same-bar contact ambiguous. MT5 Strategy Tester uses its own tick engine. Differences must be measured and documented; neither output silently replaces the other.

Trail 10 is research-only and is not a canonical Strategy A rule.