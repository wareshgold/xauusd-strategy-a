# MT5 Trailing Stop — Integration Gate

## Status

RESEARCH / EXECUTION-LAYER ONLY. No production enablement.

## Gate objective

Prove deterministic separation between local safety validation, broker-constraint validation, and the eventual MT5 modification result.

## Pipeline

`Trailing enabled`
→ `Execution contract frozen`
→ `Broker constraints valid`
→ `Request valid + favorable-only`
→ `MT5 adapter result`
→ `MODIFICATION_ACCEPTED | MODIFICATION_REJECTED`

Any failed prerequisite blocks the modification before broker submission.

## Current implementation boundary

The pipeline is executable and covered by synthetic tests, but the following remain unresolved:

- trailing distance
- activation threshold
- step size
- tick/bar evaluation cadence
- actual broker symbol constraints
- production MT5 adapter implementation

Synthetic price values are fixtures only and are not Strategy A parameters.

## Acceptance conditions before production adapter work

- CI build and tests green on the branch head.
- All local safety gates deterministic.
- Broker constraints supplied by the MT5 runtime, not guessed.
- Favorable-only stop movement invariant tested for BUY and SELL.
- Broker acceptance and rejection paths separately observable.
- Trailing remains OFF by default.
