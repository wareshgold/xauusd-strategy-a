# SP2L V3.1 Professional Account Dashboard V3

## Existing-terminal mode

V3 uses the same MT5 terminal executable already used by the Forward Runner. No second terminal installation or portable copy is required.

1. Keep the existing MT5 terminal running and logged in to the intended demo account.
2. In a separate PowerShell window, set both paths to the existing terminal:
   
   $env:SP2L_OBSERVER_TERMINAL_PATH = 'C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe'
   $env:SP2L_RUNNER_TERMINAL_PATH = 'C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe'
   $env:SP2L_OBSERVER_PORT = '8793'

3. Run from the V3 worktree:

   python scripts\\sp2l_v31_professional_account_dashboard_v3.py

4. Open http://127.0.0.1:8793.

The observer calls MetaTrader5.initialize(path=..., portable=False) to attach to the normal existing terminal data folder. It does not call MetaTrader5.shutdown() because the terminal is shared with the Runner. The observer is a separate Python process and uses only read APIs. It does not import the Runner or read/write Runner state and event files.

**Important limitation:** MT5's Python IPC is shared with the same terminal. Although this implementation avoids terminal shutdown and all trading APIs, MetaQuotes does not provide a general isolation guarantee for concurrent Python clients. Run the local smoke test first and verify Runner PIDs and order activity remain unchanged. If the terminal reports IPC contention or the Runner shows any connection error, stop the dashboard process only; do not restart the Runner.

## Read-only surface

The observer calls only account_info, positions_get, orders_get and history_deals_get. No order placement, modification, deletion, SL/TP update, or Runner module import exists in the observer. It does not read or write Runner state/event files.

## Performance definitions

- A closed trade is a position ID with at least one exit deal (entry 1 or 3) in the selected symbol history.
- Partial fills are aggregated by position ID.
- Realized net = sum of profit + commission + swap + fee across the position's symbol deals.
- Win/loss/breakeven are mutually exclusive.
- The cumulative realized-net curve is shown only at 6 or more closed positions. This is not a tick-by-tick broker equity curve.
- Drawdown is peak-to-trough drawdown of the cumulative realized-net curve, in account currency.
- Account Balance, Equity, Floating P&L, Margin and Free Margin are live account fields from MT5.

The dashboard is a research/demo operational display, not a strategy decision engine. It does not generate BUY/SELL recommendations.

## Known limitations / local acceptance

- MT5 terminal, Python package MetaTrader5, Flask and a logged-in demo account are required on the user's Windows machine.
- History is limited to the most recent 90 days.
- Confirm the observer terminal is connected to the intended demo account before trusting displayed values.
- Local Windows smoke testing, correct account/server confirmation, and confirmation that Runner PIDs and activity remain unchanged are required before treating V3 as accepted.
- V3 is not deployed and does not replace ports 8791 or 8792.