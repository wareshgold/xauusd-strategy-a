# SP2L Strategy A V2 Research Snapshot — 2026-09-27

## Snapshot purpose
Durable checkpoint of the current SP2L V2 research state. Research-only; not canonical and not production.

## Current branch
`research/sp2l-strategy-a-v2-2026-09-27`

## Preserved reference checkpoint
Exact V2 MT5 reference replay:
- 222 signals
- 204 trades
- 127 wins / 77 losses
- +50R
- 62.2549% WR
- max DD 6R
- signal ledger hash: `16ab4e1a59859809c4c230fad0431dd4040c1ad9f15b58d5b6f6f5ce12481c80`
- detector blob: `3cb93ad5cfb5b743213e8bceb1db2e440b57086a`
- reference runner commit: `a836ed038ae84a401b32dfc27690ddb04044de01`

## Controlled baseline
Dedicated V2 MT5 source baseline:
- 227 signals
- 220 decisive
- 124W / 96L
- 5 ambiguous / 2 no-fill
- +28R
- runner blob: `4f5ccc6316cbcf88d6156f431969a93fcce237ef`

## Population reconciliation
Commit `7deadc3e11acde2da85d12f44b19c027f1c354a0` and subsequent collision forensics established:
- 222 common fingerprints
- 5 baseline-only
- 0 reference-only
- no duplicate fingerprints
- all 5 baseline-only rows collide with an already-occupied reference entry_index
- collision outcome reconciliation: baseline-only collision R = +1R; matched reference occupants R = +1R; delta = 0R
- therefore the 5-row population delta does not explain the performance gap

## Common-222 outcome forensic
Tool commit: `aba3a67bd4f27e65cfaff4124e256670458ea9f6`
Run result:
- common signals: 222
- outcome semantic differences: 204
- reference trade not matched: 18
- baseline common R: +27R
- reference common R reported by current comparator: +50R
- current comparator delta: +23R

## Audit warning
The +23R is NOT yet accepted as the explanation of the total +22R gap.
The current comparator incorrectly assumes a persisted reference `activation_time` field; that field is not established by the documented reference trade schema. Therefore its fill-time classifications are not yet authoritative.

Also, the common-reference R membership must be reconciled explicitly against the complete reference +50R total and the collision-occupant population before interpreting causality.

## Exact next step
Harden the comparator:
1. inspect exact persisted reference `trades_detail` fields;
2. use only a field actually persisted by the reference runner for fill/activation timing;
3. verify one-to-one signal↔trade fingerprint membership;
4. partition reference trades into common signals vs collision occupants;
5. reconcile R sums exactly to the reference report total;
6. then classify genuine fill, exit, same-bar, no-fill, and R differences.

## Non-negotiable research constraints
- Source meaning outranks backtest performance.
- No guessed canonical P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules.
- Unresolved geometry remains unresolved.
- Neither 222 nor 227 is canonical.
- No performance-based promotion.
- Fresh holdout remains downstream of frozen geometry and validated rules.

Search tokens: SP2L_V2_RESEARCH_SNAPSHOT_20260927, COMMON_222, +50R, +28R, +22R, aba3a67, ef24a771
