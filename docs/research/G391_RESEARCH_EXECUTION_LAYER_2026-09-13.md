# G391 — Research Execution Layer

## Status

**INFRASTRUCTURE READY; CANONICAL EXECUTION BLOCKED.**

The runner now has a strategy-adapter boundary. A strategy adapter can inspect candles and return explicitly noncanonical research candidates, while the current unresolved-geometry adapter returns none.

## Safety invariants

- raw candles are not mutated;
- dataset validation remains upstream;
- split assignment remains chronological;
- candidate provenance must carry rule IDs;
- canonical candidates cannot be produced by the unresolved-geometry adapter;
- no profitability claim is made.

## Promotion boundary

Only a future source-confirmed, frozen Strategy A adapter may be eligible for canonical DEV. The current adapter is explicitly `SP2L-UNRESOLVED-GEOMETRY` and `canonical=false`.

## Next meaningful gate

Do not create further infrastructure-only G steps merely for numbering. The next substantive work should either resolve missing authoritative geometry or, if a frozen specification becomes available, instantiate its adapter and begin the controlled DEV gate.
