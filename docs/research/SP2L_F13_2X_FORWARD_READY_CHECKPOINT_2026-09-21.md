# SP2L F13 2X Forward-Ready Checkpoint — 2026-09-21

## Status

- Branch: `research/sp2l-f13-2x-forward-ready-2026-09-21`
- PR: #258
- Head commit before this checkpoint: `8c5162025658a61bb7b09aef01fde685799c5d18`
- CI Run #189: PASS
- Forward Test: previous run remains UNTOUCHED
- Production: DISABLED

## Source-confirmed change

The author-controlled source supports the secondary 2X entry relationship:

`SecondaryEntry = Entry + 0.5 * (StopLoss - Entry)`

The relationship is represented in the forward-ready replica.

## Guarded unresolved semantics

The following remain non-canonical and are not executed independently:

- 2X activation/fill semantics
- pending-order lifecycle
- risk/sizing binding
- shared/separate SL behavior
- TP allocation/closure
- replacement/cancellation precedence

## Validation

CI Run #189 completed successfully:

- Typecheck: PASS
- SP2L validation harness: PASS
- Author Replica research backtest: PASS
- Condition diagnostics: PASS
- Near-miss forensics: PASS
- Artifact upload: PASS

## Next action

A NEW research-only Forward Test may be started from this branch. The existing Forward Test process must not be modified or restarted retroactively. A new run is required to consume this version.
