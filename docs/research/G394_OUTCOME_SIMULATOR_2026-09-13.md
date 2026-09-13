# G394 — Research Outcome Simulator — 2026-09-13

## Status

**RESEARCH INFRASTRUCTURE READY / CANONICAL STRATEGY BLOCKED**

G394 adds a deterministic, research-only outcome simulator for candidates whose entry, stop, and target have already been supplied by an explicit hypothesis adapter.

## Scope

- Assumes the candidate is already filled at its declared entry price.
- Evaluates subsequent OHLC bars for stop/target hits.
- Produces WIN, LOSS, TIMEOUT, or AMBIGUOUS.
- AMBIGUOUS is returned when one OHLC bar touches both stop and target; no intrabar order is invented.
- Computes holding bars plus MAE/MFE in R units.
- No Strategy A entry, P-Gap, A/B/C/D, SL, TP, or fill geometry is defined here.

## Boundary

This simulator is deliberately downstream of the unresolved geometry. It may be used to evaluate named noncanonical hypotheses, but it cannot promote any hypothesis to canonical Strategy A.

Fresh Holdout remains excluded from hypothesis batch execution.
