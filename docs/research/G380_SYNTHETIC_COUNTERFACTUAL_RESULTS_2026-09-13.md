# G380 — Synthetic Counterfactual Discrimination

Date: 2026-09-13  
Layer: `NON_CANONICAL_HYPOTHESIS`  
Status: `RESEARCH ONLY`  
Canonical Strategy A: `false`

## Objective

Execute competing, explicitly non-canonical encodings against controlled OHLC fixtures. The goal is to expose whether a proposed interpretation changes machine output under minimal controlled changes. A result of `DISTINCT` does **not** select either hypothesis; it only proves that the interpretations are not interchangeable on that fixture.

## Result

- Fixtures executed: **10**
- Expected classifications matched: **10/10**
- Distinct outcomes: **7**
- Equivalent outcomes: **3**
- Canonical promotions: **0**

## Fixture results

| Fixture | Family | A | B | Result |
|---|---|---|---|---|
| G380-PG-01 | P-Gap | PG-H01 | PG-H02 | EQUIVALENT |
| G380-PG-02 | P-Gap | PG-H01 | PG-H03 | EQUIVALENT |
| G380-PG-03 | P-Gap | PG-H03 | PG-H04 | DISTINCT |
| G380-AB-01 | A/B/C/D | ABCD-H01 | ABCD-H02 | DISTINCT |
| G380-AB-02 | A/B/C/D | ABCD-H02 | ABCD-H03 | DISTINCT |
| G380-EN-01 | Entry | EN-H01 | EN-H02 | DISTINCT |
| G380-EN-02 | Entry | EN-H02 | EN-H03 | DISTINCT |
| G380-SL-01 | SL | SL-H01 | SL-H02 | DISTINCT |
| G380-TP-01 | TP | TP-H01 | TP-H04 | DISTINCT |
| G380-TP-02 | TP | TP-H01 | TP-H04 | EQUIVALENT |

## Interpretation

The synthetic layer confirms that several unresolved dimensions are operationally consequential. In particular, candidate P-Gap timing, A/B/C/D measurement field, entry location, SL boundary, and target construction can produce different machine outputs on controlled inputs.

The equivalent cases are equally important: two different candidate encodings can collapse to the same output for a particular fixture. Therefore, a single historical example or single chart cannot identify the source rule. Discrimination requires fixtures that isolate the changed variable.

## Source boundary

These candidate formulas are research encodings only. They are not claimed to reproduce the instructor's geometry. The source remains authoritative, and G378's unresolved dimensions remain unresolved.

No historical performance data was used to choose between hypotheses. No hypothesis was promoted because it produced a desirable result.

## Gate decision

**FROZEN GEOMETRY remains BLOCKED.**

G380 passes as a synthetic research execution layer only. It does not authorize canonical DEV, VAL, live signals, or production.

## Next step

Expand the counterfactual matrix to cover the remaining hypothesis pairs from G368/G376, especially parent-vs-nested A/B/C/D scale, trigger-vs-fill timing, and target/entry coupling, then produce a consolidated discrimination matrix and determine which dimensions remain source-underdetermined versus merely implementation-distinct.
