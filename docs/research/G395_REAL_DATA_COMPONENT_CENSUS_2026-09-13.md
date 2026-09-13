# G395 — Real-Data Hypothesis Component Census — 2026-09-13

## Gate

**RESEARCH-ONLY / CANONICAL=false**

This pass executes previously documented noncanonical component formulas against the existing XAU/USD M5 dataset's DEV interval. It is deliberately a component census, not a Strategy A backtest.

## Scope

- Dataset: existing Twelve Data XAU/USD M5 snapshot.
- DEV: 2026-03-17 15:15:00Z through 2026-06-30 23:59:59Z.
- Fresh Holdout is not read or evaluated by this workflow.
- No new geometry is inferred.
- No candidate is promoted to canonical.

## Hypotheses executed

Only formulas already recorded in G380 are encoded here: PG-H01/H02/H03/H04, ABCD-H01/H02/H03, EN-H01/H02/H03, SL-H01/H02, TP-H01/TP-H04. Their presence in code does not make them Strategy A rules.

## Interpretation

The output is useful for measuring how frequently competing unresolved components occur in real DEV data and whether candidate definitions materially differ in observations. It must not be interpreted as profitability, expectancy, edge, or source confirmation.

A complete trade-level backtest remains blocked because the authoritative source has not frozen the missing P-Gap endpoints, A/B/C/D anchors, exact pending-limit price/fill semantics, exact SL boundary, and canonical target mapping.
