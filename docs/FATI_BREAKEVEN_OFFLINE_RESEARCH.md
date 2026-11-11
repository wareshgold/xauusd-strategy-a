# Fati Breakeven – Offline Research Fixtures

Status: research-only; not canonical; not connected to MT5; not used by Runner V3.1.

## User-approved design inputs

- Fixed volume: 0.01 lot.
- Commission: USD 0.05 per side, therefore USD 0.10 round trip.
- Breakeven activation: approximately 5 pips of favorable movement.
- Breakeven is the only planned exception to the fixed initial SL.
- One successful SL move per position; no trailing after it.
- TP remains separately owned and managed by Fati.
- Telegram account notifications remain limited to Pending Order and Order Filled.

## Explicit arithmetic assumptions in this fixture

The test model uses pip size 0.10 price units and contract size 100.0. At 0.01 lot:

- Value per pip = 100 × 0.01 × 0.10 = USD 0.10.
- Round-trip commission = 2 × USD 0.05 = USD 0.10.
- Commission offset = 1.0 pip = 0.10 price units.
- Five-pip activation distance = 0.50 price units.

Thus, for entry price E, the unrounded candidate SL is E + 0.10 for BUY and E - 0.10 for SELL.

These values are fixture assumptions pending confirmation against the exact Otet symbol contract, tick size, account commission ledger, and realized Demo close records. They do not account for slippage, swap, or other fees. No claim of guaranteed net-zero execution is made.

## Deliberately unresolved

The caller supplies `favorable_move_price`. This fixture does not define whether the live activation measurement is based on Bid/Ask ticks, completed-bar extremes, or another source. That execution/measurement rule must be resolved before integration.

Tick-size normalization, Stop Level/Freeze Level validation, quote-side selection, TP preservation, and broker reconciliation belong to a future Broker adapter; this module does not perform them.

## Broker response semantics

- A rejected SL request must not mark BE as confirmed.
- The decision remains eligible for a controlled retry, subject to an external retry/cooldown policy.
- Only broker-confirmed SL change may set `be_confirmed=True`.
- If the current SL is already at least as protective as the candidate BE level, no SL change is requested.
- After confirmed BE, no further SL modification is allowed by this policy.

## Offline test command

```powershell
python -m unittest tests.test_fati_breakeven_policy_research -v
```

The helper is pure Python and imports no MetaTrader5 package, Telegram client, or live Runner module. It contains no order-send API.
