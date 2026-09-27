# SP2L Strategy A Research Workflow Snapshot — 2026-09-27

## Objective
Reconstruct and validate Strategy A from source evidence without inventing canonical geometry or execution semantics.

Workflow:
SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION

Source meaning outranks backtest performance. Unresolved geometry remains unresolved. AI may assist research/engineering/analytics but does not define canonical rules or production BUY/SELL decisions.

## Current branch
`research/sp2l-strategy-a-v2-2026-09-27`

## Current forensic objective
Determine whether recurring XAUUSD MT5 M1 discontinuities can be explained by a common UTC/session boundary before any data normalization is considered.

Canonical Strategy A rules are NOT being changed by this forensic work.

## Completed forensic chain

1. Raw XAUUSD boundary audit: 58 unique unresolved non-weekend XAUUSD gaps; 57 rollover-like observations and 1 isolated OTHER outlier. Session cause remains unresolved.
2. Cross-symbol aggregate control: seven FX controls inspected at the same 58 XAUUSD intervals.
3. Case-level cross-symbol interval control: 44/58 MIXED; 6 ALL_CONTROLS_CONTINUOUS; 6 ALL_CONTROLS_PARTIAL; 2 ALL_CONTROLS_EMPTY.
4. Temporal clustering: non-mixed cases concentrated around 00:00/01:00 UTC boundaries; the 2026-09-07 case remains isolated OTHER.
5. Boundary-minute presence matrix: XAUUSD has 0/58 bars at gap-start T+0 and 0/58 at gap-end T+0; FX controls have 392/406 bars at each corresponding T+0. The XAUUSD discontinuity is therefore not established as a market-wide UTC timestamp closure.

## Current step
Run raw XAUUSD gap group audit without normalizing observed patterns:
- exact 23:59 → 01:00
- 23:58 → 01:00
- 23:59 → 00:59
- OTHER
The OTHER group must remain separate.

## Current blocker
`sp2l_xauusd_raw_gap_group_audit.py` raises a KeyError because the unique forensic artifact stores boundary fields under its actual schema rather than the fields assumed by the new script. This is a schema-alignment bug in research tooling, NOT a data conclusion.

## Next planned steps
1. Fix the group-audit script to consume the actual unique-forensics schema.
2. Re-run the group audit and commit the resulting checkpoint/artifact.
3. Inspect rollover-like group vs OTHER group at raw-bar level.
4. If evidence supports it, perform a narrowly scoped XAUUSD-only temporal consistency test.
5. Decide whether a diagnostic data-quality classification is justified.
6. Do NOT promote any session closure, gap normalization, P-Gap geometry, trigger semantics, or execution rule to canonical status from this work.

## Explicit evidence boundary
`SESSION_CAUSE=UNRESOLVED`
`SESSION_APPROVAL=NOT_ESTABLISHED`
`research_only=true`

## Strategy A source status
Source-confirmed: F12 trigger direction; F13 2X; F10 stop concept; F14 AB=CD concept; TP default 1:1.
Still unresolved: exact P-Gap formula/candle roles; trigger acceptance/indexing/entry/fill semantics; exact SL boundary/buffer; F13 lifecycle; F14 anchors/tolerance.