# Order and Deal Lifecycle Evidence Contract — 2026-10-26

## Source basis

The research runner's `order_state_name` maps broker order states into STARTED, PLACED, CANCELED, PARTIAL, FILLED, REJECTED, EXPIRED, REQUEST_ADD, REQUEST_MODIFY, REQUEST_CANCEL, or an explicit UNKNOWN label. Its pending-order lifecycle logger records order state and order fields. Separately, `monitor_symbol_lifecycle` reads broker deal history and logs deal tickets, order tickets, position IDs, entry classification, volume and financial fields.

Those are distinct source paths. An order-state observation is not a deal record; a deal record is not proof that the entire requested order volume filled.

## Factory fixture contract

`src/strategy_factory/source_order_lifecycle.py` classifies only supplied observations:

- PLACED and other nonterminal states remain ORDER_STATE_ONLY.
- PARTIAL without initial/current volume evidence is UNRESOLVED.
- PARTIAL with valid volume fields records that the broker exposed a partial-order state; it does not synthesize a deal.
- FILLED/CANCELED/REJECTED/EXPIRED are terminal order-state observations, not substitutes for a deal ledger.
- A supplied deal with a recognized entry class is DEAL_RECORDED while order completion remains un-inferred.
- Unknown states, unknown deal-entry classes, missing records and invalid identifiers/volumes stay UNRESOLVED.

The fixture does not decide how a broker may split fills, reconcile delayed history, interpret missing observations, or map all platform-specific return codes. It never creates a fill from a theoretical entry, candle touch, or order state alone.

## Regression coverage

Tests cover PLACED without fill, PARTIAL without volumes, PARTIAL with remaining volume, FILLED without a deal ledger, a deal alongside a PARTIAL order, distinct IN/OUT deal classes, unknown state/class, missing observations, and invalid volume relationships. These are synthetic contract tests, not a real MT5 connection or a historical execution replay.

## Replay gate

Replay remains BLOCKED. This contract improves event labeling but does not resolve partial-fill accounting across multiple deal tickets, event timing/order, rejected/canceled race behavior, actual entry price and cost attribution, or the immutable source-data binding. Those require source review and broker-record evidence before statistical outcomes can be trusted.
