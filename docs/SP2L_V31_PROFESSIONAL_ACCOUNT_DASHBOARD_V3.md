# SP2L V3.1 Professional Account Dashboard V3

## Isolation requirement

V3 is a separate read-only observer process. It must use a separate MT5 terminal installation/copy in portable mode, not the terminal used by the Forward Runner.

1. Copy the complete MT5 terminal installation to a separate writable folder, for example D:\MT5-Observer\.
2. Keep the existing Runner terminal at C:\Program Files\Otet Group MT5 Terminal\terminal64.exe.
3. Start the copied terminal once, log in to the intended demo account, and confirm the account/server. Do not use the same terminal executable path as the Runner.
4. In a separate PowerShell window, set:

   $env:SP2L_OBSERVER_TERMINAL_PATH = 'D:\MT5-Observer\terminal64.exe'
   $env:SP2L_RUNNER_TERMINAL_PATH = 'C:\Program Files\Otet Group MT5 Terminal\terminal64.exe'
   $env:SP2L_OBSERVER_PORT = '8793'

5. Run from the isolated V3 worktree:

   python scripts\sp2l_v31_professional_account_dashboard_v3.py

6. Open http://127.0.0.1:8793.

The script requires an explicit observer terminal path and refuses the known Runner terminal path. It initializes the observer terminal with portable=True, binds the web server to localhost, and shuts down only the observer connection when its own process exits. Do not configure the Runner terminal path as the observer path.

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
- Local Windows smoke testing and confirmation that Runner PIDs remain unchanged are required before treating V3 as accepted.
- V3 is not deployed and does not replace ports 8791 or 8792.