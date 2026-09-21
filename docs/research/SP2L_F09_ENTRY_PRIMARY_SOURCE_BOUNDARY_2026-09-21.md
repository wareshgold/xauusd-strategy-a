# SP2L F09 Entry Primary-Source Boundary — 2026-09-21

## Source-confirmed boundary

Existing archived source evidence confirms:
- the entry mechanism is presented as a Pending Limit setup;
- the corrective development can occur across a family of 1-, 2-, or 3-candle developments;
- the source does not require a single universal candle count.

## Still unresolved

The available primary-source record does not uniquely determine:
- exact pending-order price field;
- exact candle/index used for that price;
- precedence between a pending-limit placement and a later reclaim/trigger interpretation;
- replacement/update precedence when correction structure evolves;
- exact touch/breach/close semantics for activation/fill.

## Implementation alignment

Current `EntryTrigger.ts` uses a post-correction close reclaim and sets entryPrice to the reclaim candle close. This is a research hypothesis, not a source-confirmed canonical rule.

## Decision

- F09 source concept: SOURCE-CONFIRMED-PARTIAL
- Exact executable entry geometry: UNRESOLVED
- Current close-reclaim implementation: NON-CANONICAL
- Backtest selection: PROHIBITED
- Frozen Geometry: BLOCKED
- Production: DISABLED
