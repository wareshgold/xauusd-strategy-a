# Fati Execution Adapter — Pre-Login Technical Design

Status: design-only; offline implementation gate.
Broker: Otet (user-provided).
Account: described as similar to the primary Runner account; not yet independently verified.
Canonical: no.
MT5 connection: not authorized before the separately scheduled session.
Order execution: not authorized.

## 1. User-approved Fati behavior

- Initial position has no TP (TP=0).
- Initial SL is supplied by the upstream approved signal and becomes the immutable initial-risk anchor after fill.
- RR1 is measured from the actual broker fill against the original SL.
- At RR1, request exactly one SL move to BE+5 pips.
- BUY target: actual fill + 5 pips.
- SELL target: actual fill - 5 pips.
- No trailing, second SL adjustment, automatic TP, or automatic close.
- After the one permitted SL adjustment, position management belongs to Fati; manual TP/close actions are outside this adapter.
- Fati notifications are isolated: Pending Order and Order Filled only. No Fati trade outcomes/results to the private Fati destination; no routing into the primary Runner channel.

## 2. Strict component boundaries

### Allowed responsibilities
- Validate an already-approved signal without generating BUY/SELL decisions.
- Submit the Fati initial order with TP=0 only after a separately authorized execution phase.
- Reconcile actual fills and broker positions.
- Evaluate RR1 from an explicit, externally resolved price observation.
- Request one BE+5 SL modification.
- Reconcile the broker response and persist the confirmed state.
- Emit only the two approved Fati notification types.

### Forbidden responsibilities
- Define or modify SP2L/Strategy A geometry.
- Infer pip size, quote side, or RR1 sampling semantics.
- Reuse primary Runner state, lock, Magic, Telegram routing, or V3.1 trailing code.
- Manage TP, trail SL, make a second SL modification, or close positions.
- Connect to MT5 before explicit user authorization.
- Treat a locally submitted SL request as broker-confirmed.

## 3. Proposed adapter interfaces

The offline core should depend on narrow interfaces, not directly on MetaTrader5:

- `SignalSource`: supplies an already-approved signal and its immutable initial SL.
- `BrokerPort`: abstract operations for submitting an order, reading orders/deals/positions, and requesting an SL modification.
- `QuoteObservation`: carries a price observation plus its declared source/side/timestamp. The core must reject an observation whose semantics are not configured and approved.
- `StateRepository`: durable load/save with atomic update semantics.
- `EventJournal`: append-only event records with stable identifiers.
- `FatiNotifier`: allow-listed Pending Order and Order Filled events only.

No concrete MT5 implementation should be added until account-specific specifications and quote semantics are approved.

## 4. State machine

Proposed states:

1. SIGNAL_ACCEPTED
2. ORDER_SUBMITTED
3. ORDER_CONFIRMED
4. FILL_PENDING
5. POSITION_RECONCILED
6. WAITING_FOR_RR1
7. BE_REQUEST_PENDING
8. BE_CONFIRMED
9. MANUAL_MANAGEMENT
10. RECONCILIATION_REQUIRED
11. HALTED

Safety transitions:
- No actual Fill confirmation => no RR1 monitoring.
- No valid RR1 observation => no SL modification request.
- After sending an SL request, persist BE_REQUEST_PENDING before any further action.
- Only broker-confirmed resulting SL can transition to BE_CONFIRMED.
- Unknown request outcome => reconcile broker state first; never blindly resubmit.
- Mismatch between local state and broker position => RECONCILIATION_REQUIRED.
- Missing/invalid account profile or quote semantics => HALTED.
- BE_CONFIRMED => no further automated SL/TP/close actions.

## 5. Immutable trade anchors

For each position, persist:
- Fati account/server identity (sanitized; never credentials).
- Exact symbol and symbol-specification fingerprint.
- Unique signal, order, deal, and position identifiers.
- Direction and filled volume.
- Actual fill price or a documented volume-weighted fill aggregation rule.
- Immutable initial SL.
- Verified pip-size conversion and its provenance.
- RR1 observation source, quote side, sampling rule, and timestamp.
- BE+5 target.
- SL request identifier, broker response, and confirmed resulting SL.
- State transition sequence and event-journal sequence.

Partial fills, multiple deals, netting/hedging behavior, and position aggregation must be explicitly specified before implementation; do not silently choose a rule.

## 6. Idempotency and restart recovery

- A stable position key must include account/server context, symbol, Magic, and broker position identity.
- Every outbound modification must have a durable intent record before sending.
- A restart in BE_REQUEST_PENDING must reconcile the broker's current position and SL before deciding anything.
- A missing position, changed position identity, or unresolvable order/deal relation must halt that position's automation.
- Duplicate events must not create duplicate notifications or SL requests.
- Corrupt or unreadable state must fail closed; no automatic state recreation from assumptions.

## 7. Account profile and fail-closed configuration

The runtime profile must require explicit values for:
- Exact account server/type and account currency.
- Exact symbol name/suffix.
- Digits, point, tick size, tick value, contract size.
- Volume min/max/step.
- Stops level, freeze level, execution/filling mode, supported order types.
- Commission amount, currency, and charging convention.
- Pip-size conversion for BE+5.
- RR1 quote side, sampling rule, spread treatment, and staleness threshold.

Missing values must prevent enablement. No defaults may be inferred from the Runner or public website.

## 8. Offline validation before account access

Required mock-based tests:
- Initial order request always has TP=0.
- BUY/SELL RR1 and BE+5 calculations using synthetic fixtures only.
- Actual fill rather than requested entry is used.
- Partial/multiple fills cannot be silently misaggregated.
- One and only one SL request can be pending/confirmed per position.
- Rejected/unknown broker response is not marked confirmed.
- Better existing SL is never loosened.
- Stop/freeze rejection fails closed.
- Restart recovery from every state.
- Corrupt state, duplicate events, missing positions, and account mismatch halt safely.
- No calls to primary Runner modules, state, lock, Magic, or Telegram route.
- Notification allow-list rejects trade outcomes/results.
- Missing account profile or quote semantics blocks the adapter.

The existing 18 policy-helper tests are a separate unit-test layer; they do not validate this adapter, MT5 integration, or broker behavior.

## 9. Otet evidence boundary

See `FATI_OTET_BROKER_READINESS.md`. Public Otet web values are reference evidence only. The exact Fati terminal symbol and account-specific values remain unverified until the user authorizes access.

## 10. Explicit pre-Monday scope

Permitted:
- Implement and test pure offline state-machine logic.
- Implement a mock BrokerPort and synthetic event journal.
- Validate config schema and fail-closed behavior.
- Run offline unit tests, static checks, and isolation checks.

Not permitted:
- Ask for or store login credentials/verification code.
- Initialize or connect an MT5 terminal.
- Read or modify live/demo orders or positions.
- Send an order or SL/TP modification.
- Add Fati to the running primary Runner.
- Declare the adapter production-ready.

## 11. Gate for the separately authorized connection session

At the scheduled session, after the user provides access:
1. Identify the exact Fati terminal/server/account context.
2. Capture a sanitized symbol/account specification snapshot.
3. Compare it field-by-field with the primary Runner reference snapshot.
4. Resolve pip conversion and RR1 quote semantics explicitly.
5. Confirm order/position/fill reconciliation behavior.
6. Confirm stop/freeze and SL-modification response handling.
7. Run read-only diagnostics first.
8. Only then present a separate, explicit authorization request for any Demo rehearsal or Runner integration.

Passing this gate does not itself authorize trading.
