# SP2L MT5 Session Matrix Gate — 2026-09-21

## Final state for this stage

The raw MT5 session matrix and cross-window provenance audit are complete at the observation layer.

### PASS
- raw timestamp preservation;
- M1 availability/gap inventory;
- weekday/hour distribution capability;
- provenance metadata retention;
- no-lookahead/data-integrity guard compatibility.

### BLOCKED
- fixed UTC offset;
- historical timestamp basis;
- canonical London/New York session labels;
- production/fresh-holdout session filtering.

## Reason
The observed terminal-versus-UTC relationship is evidence of an offset-like mapping in the tested environment, not sufficient proof of a universal historical mapping.

## Decision
Do not convert or relabel MT5 historical bars as UTC/session-normalized data until independent terminal/server time evidence closes the mapping gate.

## Strategy impact
No Strategy A geometry or execution rule is changed. Frozen Geometry remains blocked independently by source-resolution blockers.

## Next track
Proceed with noncanonical MT5 engineering or obtain independent terminal/server timestamp evidence. Once the time-basis gate is closed, rebuild the session matrix from raw data without changing candle semantics.
