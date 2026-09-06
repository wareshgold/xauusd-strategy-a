# Phase 10C — Early-MAE Recovery / Failure State Transition

## Objective
Determine whether early adverse excursion states contain information about subsequent recovery/failure, without creating an exit rule or optimizing thresholds.

## Scope
- Dataset: existing 5m Strategy A pre-holdout universe.
- Population: 144 canonical DELAY1 trades.
- DEV/VAL split: DEV entryIndex < 6000; VAL 6000 <= entryIndex < 10000.
- Fresh holdout: LOCKED and excluded.
- Horizons: T3, T5, T10.
- States: <0.25R, 0.25–0.50R, 0.50–0.75R, 0.75–1.00R, >=1.00R.

## Questions
1. Within each fixed early-MAE state, how often does the trade later reach MFE >= 1R or >= 2R?
2. Does an early adverse state transition toward a less-adverse state by the next fixed horizon?
3. Among trades reaching >=1R adverse excursion, how often do they later recover to MFE >=1R or >=2R?
4. Do the descriptive outcome patterns replicate between DEV and VAL?

## Methodological constraints
- No threshold optimization.
- No best-state selection.
- No new session/time partitioning.
- No broker execution model.
- No exit, break-even, trailing-stop, TP, or SL rule creation.
- Canonical final rMultiple remains the outcome variable.
- Existing fixed MAE/MFE horizons are used only for diagnostics.
- Production strategy files remain untouched.

## Interpretation rule
A replicated state association is evidence for further research only. It is not a validated trading rule and must not be converted directly into an exit decision.

## Next gate
If recovery/failure patterns replicate and show economically meaningful separation, a later phase may model actual first-threshold breach exit economics using path prices. That phase must be explicitly approved as an exit-rule experiment and must remain pre-holdout until the rule is frozen.
