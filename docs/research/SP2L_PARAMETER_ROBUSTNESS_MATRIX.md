# SP2L Author Replica — Parameter Robustness Matrix

Status: research-only; not canonical Strategy A.

Purpose: test sensitivity around the existing author-replica baseline without changing source interpretation or defining canonical geometry.

Baseline:
- P-Gap price 1.0
- Spike multiplier 1.5
- Max SL price 10.0
- TP 1R
- XAUUSD.ecn, M1
- Four Mon-Fri windows: 2026-08-24 through 2026-09-18

The runner evaluates 81 combinations:
- P-Gap price: 0.8 / 1.0 / 1.2
- Spike multiplier: 1.3 / 1.5 / 1.7
- Max SL price: 8 / 10 / 12
- TP: 0.8R / 1.0R / 1.2R

Metrics include pooled decisive WR, total R, PF, signal/outcome counts, minimum and maximum weekly WR, and weekly WR for each combination.

Interpretation is diagnostic only. A broad neighborhood of similar results supports robustness; an isolated peak indicates sensitivity. No observed result is used to promote a canonical parameter.

The runner preserves the existing MT5 acquisition pattern (copy_rates_from, 10,000 M1 bars per week). Historical timestamp semantics and broker/session coverage therefore remain separate validation concerns.

This matrix does not unlock Frozen Geometry, Untouched Validation, Fresh Holdout, or Production. Source resolution and unresolved execution/fill semantics remain independent gates.
