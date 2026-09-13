# G379 — Non-Canonical Hypothesis Execution

Date: 2026-09-13  
Gate: `SOURCE_RESOLUTION -> NON-CANONICAL HYPOTHESIS LAYER`  
Status: `RESEARCH ONLY`  
Canonical Strategy A: `false`

## 1. Purpose

G379 operationalizes the already-approved hypothesis layer after G378 closed the currently available authoritative-source search without resolving executable geometry. It does **not** freeze Strategy A and does **not** authorize historical optimization, DEV promotion, live signals, or production use.

The machine registry contains 23 distinct candidate hypotheses already defined by G368 across five families: P-Gap, A/B/C/D, Entry, Stop, and Target.

## 2. Deterministic guardrails

The implementation enforces four conditions:

1. The registry must contain exactly the expected 23 IDs with no duplicates.
2. Every hypothesis must remain `canonical=false`.
3. At least one executable geometry dimension must remain explicitly unresolved.
4. The gate decision must therefore remain `FROZEN-GEOMETRY-BLOCKED`.

These are safety properties for research, not trading rules.

## 3. Registry coverage

| Family | IDs | Count | State |
|---|---|---:|---|
| P-Gap | PG-H01..PG-H04 | 4 | non-canonical |
| A/B/C/D | ABCD-H01..ABCD-H06 | 6 | non-canonical |
| Entry | EN-H01..EN-H04 | 4 | non-canonical |
| Stop | SL-H01..SL-H04 | 4 | non-canonical |
| Target | TP-H01..TP-H05 | 5 | non-canonical |
| **Total** | | **23** | **blocked** |

## 4. What was executed

The machine test checks registry completeness, uniqueness, canonical=false invariants, and unresolved-geometry persistence. This is intentionally narrower than a historical backtest: no market data is used to infer source meaning.

The existing G376 minimal-pair suite remains the discrimination evidence for the candidate dimensions. Its classifications are preserved rather than reinterpreted:

- P-Gap: endpoint indexing, wick/body overlap, pressure context, and timing variants remain distinct or underdetermined as previously classified.
- A/B/C/D: anchor type, wick/body field, correction depth, and parent-vs-nested scale remain discriminating dimensions.
- Entry: trigger/fill and C timing remain distinct or underdetermined; `fill_price == C` is not assumed.
- Stop: origin wick/body and invalidation boundary remain distinct.
- Target: AB=CD versus official default 1:1 remains a source-reconciliation conflict requiring further authoritative evidence; TP1/TP2 mapping remains unresolved.

## 5. Gate result

**FROZEN GEOMETRY: BLOCKED.**

G379 is a successful research-layer execution because the guardrail behaves correctly: unresolved source geometry cannot silently become a canonical implementation.

No DEV/VAL/fresh-holdout backtest is promoted by this gate.

## 6. Next permitted work

The next permitted work is further **non-canonical synthetic discrimination** only, using explicit fixture data to determine whether candidate encodings produce materially different machine outputs. Any candidate that cannot be resolved by source remains a research hypothesis regardless of historical performance.

A new authoritative artifact can reopen SOURCE RESOLUTION at any time. Until then, no canonical P-Gap formula, A/B/C/D anchor, exact pending-limit price/fill semantics, SL offset/boundary, or TP mapping may be invented.
