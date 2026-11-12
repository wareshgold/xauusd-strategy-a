# Fati RR1 -> BE+5, no-TP research contract

Status: research-only design fixture. Not approved for live/demo execution.

## User-defined behavior

- Initial order has no take-profit: requested TP value is 0.
- The position starts with its initial stop-loss.
- At RR1, move the stop-loss once to BE+5 pips.
- BUY target: actual fill price + 5 pips.
- SELL target: actual fill price - 5 pips.
- No trailing, second stop adjustment, automatic TP, or automatic close.
- After the one permitted stop adjustment, position management belongs to Fati.
  Fati may close manually or place/change a TP manually in MT5.

## Research helper boundary

`scripts/fati_rr1_be5_no_tp_policy_research.py` is pure arithmetic/decision
logic. It does not import MT5, connect to a terminal, submit/modify/cancel
orders, close positions, manage TP, send Telegram, or implement trailing.

The helper requires an explicit `pip_size_price`; it intentionally has no
XAUUSD pip-size default. Its tests use 0.10 only as a synthetic fixture, not as
a broker specification.

The RR1 evaluator receives:
- actual fill price;
- immutable initial SL price;
- current SL price;
- favorable movement in price units;
- broker-confirmed one-time-change state.

It calculates initial risk from actual fill to the original SL. The source of
`favorable_move_price` (Bid/Ask, tick stream, or another quote convention)
is deliberately not defined by this helper.

## Unresolved before any execution adapter

1. Verify the exact account's XAUUSD.ecn contract size, tick size, tick value,
   digits, volume constraints, stop level, freeze level, and commission.
2. Verify pip-size conversion for that exact symbol/account. Do not copy the
   synthetic fixture value into runtime configuration.
3. Resolve which live quote side and sampling semantics produce favorable
   movement for BUY and SELL, including spread effects.
4. Specify broker rejection/reconciliation behavior. A rejected modification
   must not be treated as confirmed. Before any retry, reconcile the actual
   broker position and current SL to avoid duplicate or stale requests.
5. Verify that the BE+5 target is valid against broker stop/freeze constraints
   at the RR1 moment. If invalid, fail closed: no alternative SL, no trailing,
   and no repeated blind requests.
6. Keep the Fati terminal, account identity, runtime/state/events, lock, magic,
   and Telegram destination isolated from the primary Runner.

## Explicit exclusions

- No MT5 terminal/account connection or credential handling.
- No live or demo order execution.
- No change to the primary Runner, its configuration, state, events, or Telegram.
- No reuse of V3.1 trailing modules.
- No canonical SP2L geometry decision.
- No claim that this research helper has passed local CI merely because its
  source and test fixtures have been committed.

## Validation sequence

Run the focused offline test module first, then the repository test suite.
Review the diff and test results before considering any execution adapter.
A separate authorization and broker-spec audit are required before connecting
the Fati account.
