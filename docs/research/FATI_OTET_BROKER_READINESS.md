# Fati / Otet Broker Readiness Record

Status: pre-connection research; no account login performed.
Account owner will provide the login/verification code only when explicitly scheduling the Fati connection. Until then, no MT5 initialization, account selection, market request, order request, or trade action is authorized.

## User-provided account context

- Broker: Otet.
- Fati account is described by the user as similar to the Otet account currently used by the running primary Runner.
- The user expects the remaining account-access step to be providing the login verification code.
- This similarity is useful as a comparison lead, not proof that Fati has identical account group, server, symbol suffix, contract specification, commission schedule, or execution restrictions.
- The Fati account is not to be connected until the user explicitly authorizes the planned Monday session.

## Public Otet evidence reviewed

1. Otet's public XAU/USD symbol page identifies the instrument but currently renders contract size, point size, minimum volume, and maximum volume as unavailable ("—"). It is not an account-specific MT5 specification:
   https://otetmarkets.com/symbol/xauusd/

2. Otet's metals page currently publishes XAU/USD with contract size 100, point 0.01, and volume 0.01–100 lots. The page also warns that live market data can be temporarily unavailable. This is a public website listing for XAU/USD, not proof for the terminal symbol XAUUSD.ecn or Fati's account:
   https://otetmarkets.com/metals-assets/

3. Otet's account comparison lists different commission schedules by account type (including ECN, ECN+, Festival, Social Trade and others). The public account page therefore does not establish Fati's commission until the exact account type is confirmed:
   https://otetmarkets.com/accounts/

4. Otet's Terms and Conditions state that contract specifications are available in the client terminal; define freeze level and stop/limit levels; and describe the possibility of freeze levels being set dynamically. This supports checking the live terminal values rather than hardcoding website values:
   https://otetmarkets.com/terms-and-conditions/

5. Otet's published terms state that chart prices are Bid-based and that BUY transactions execute at Ask while SELL transactions execute at Bid. This does not, by itself, settle the precise quote-side/sampling convention for Fati's RR1 trigger; that remains an explicit implementation decision:
   https://otetmarkets.com/terms-and-conditions/

## What is not verified

The following must remain unset/unapproved until captured from Fati's own logged-in terminal, or otherwise confirmed by authoritative account-specific documentation:

- Account login identity and server (never store password or verification code in repository).
- Exact account group/type and account currency.
- Exact gold symbol name/suffix (e.g. whether it is XAUUSD.ecn).
- Digits, point, tick size, tick value, contract size.
- Minimum/maximum volume and volume step.
- Stops level and freeze level.
- Filling/execution mode and supported order types.
- Commission amount, currency, and whether quoted per side or round turn.
- Pip-size conversion for the explicit BE+5 policy.
- RR1 quote side and sampling rule, including spread handling.
- Broker confirmation/reconciliation behavior for SL modifications.

## Runner comparison protocol (read-only, later)

When the user authorizes account access, collect a sanitized snapshot from the Fati terminal and compare it field-by-field with a previously captured Runner account snapshot. Do not infer equality from account-type labels alone.

Comparison result for each field must be one of:
- MATCH: same value, same symbol identity, same account/server context.
- DIFFERENT: values differ.
- UNKNOWN: unavailable or not captured.

Any UNKNOWN or DIFFERENT value relevant to price conversion, order validity, or execution must block runtime enablement until resolved.

## No-login preparation allowed before Monday

- Offline unit tests and mock-based adapter tests.
- State-machine and persistence/recovery tests using synthetic fixtures.
- Configuration validation that fails closed when account-specific values are missing.
- Documentation, static analysis, and repository isolation checks.

## Explicitly prohibited before separate authorization

- Requesting, storing, or using the login verification code.
- Connecting to MT5 or selecting a terminal/account.
- Reading or changing live positions/orders.
- Sending demo/live orders or modifying SL/TP.
- Integrating Fati into the active primary Runner.
- Reusing primary Runner state, magic, locks, Telegram routing, or V3.1 trailing modules.

## Readiness gate

Fati may be considered ready for a separately authorized connection session only after offline code and mock tests pass. It must not be called ready for trading. Account-specific configuration, quote semantics, broker constraints, and a separately approved integration/rehearsal remain outstanding.
