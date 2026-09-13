# G375 — Hypothesis Execution Result Matrix

Date: 2026-09-13
Status: RESEARCH ONLY / canonical=false

## Scope

This artifact operationalizes the existing G369 minimal-pair design as a deterministic research classification matrix. It does **not** define Strategy A production rules, does not optimize parameters, and does not use historical profitability to promote a hypothesis.

## Result classes

- `DISTINCT`: the two hypotheses can produce different deterministic outputs when the isolated variable changes.
- `EQUIVALENT`: source evidence currently permits both as semantically compatible descriptions of the same observed form; no executable geometry is selected.
- `SOURCE-CONFLICT`: authoritative materials currently state competing target/exit semantics that have not been reconciled.
- `UNDERDETERMINED`: source evidence is insufficient to select one executable interpretation.

## Executed matrix

| Fixture | Family | Isolated variable | Result | Source-safe conclusion |
|---|---|---|---|---|
| PG-MP-01 | PGAP | gap endpoint indexing | UNDERDETERMINED | Pressure Gap is confirmed; executable endpoints are not labeled. |
| PG-MP-02 | PGAP | wick/body overlap | UNDERDETERMINED | No P-Gap wick/body overlap rule is source-confirmed. |
| PG-MP-03 | PGAP | weak range vs sustained pressure | DISTINCT | Pressure Gap is contextualized by sustained directional pressure; generic range gap is not equivalent. |
| PG-MP-04 | PGAP | timing variant | EQUIVALENT | Breakout→FT→gap and higher-structure→gap are both source-observed variants. |
| AB-MP-01 | ABCD | swing extreme vs candle boundary | DISTINCT | Anchor choice changes measured Leg 1. |
| AB-MP-02 | ABCD | wick extreme vs body/close | DISTINCT | OHLC-field choice changes geometric measurement. |
| AB-MP-03 | ABCD | shallow vs deep parent correction | DISTINCT | Source demonstrates nested/parent scale distinctions. |
| AB-MP-04 | ABCD | nested vs parent leg | DISTINCT | Parent and nested 2Leg structures are materially different scales. |
| EN-MP-01 | ENTRY | trigger vs later fill | DISTINCT | Pending-limit activation and actual execution must remain separate states. |
| EN-MP-02 | ENTRY | C touched before/after trigger | UNDERDETERMINED | C is not source-confirmed as the fill or trigger price. |
| EN-MP-03 | ENTRY | unfilled pending limit vs trigger condition | DISTINCT | Pending-limit semantics cannot be replaced by a market-trigger assumption. |
| SL-MP-01 | SL | wick vs body origin boundary | DISTINCT | Different candle fields yield different stop prices; source does not select one. |
| SL-MP-02 | SL | origin extreme vs structural invalidation | UNDERDETERMINED | Structural invalidation is supported, exact price boundary is not. |
| TP-MP-01 | TP | AB=CD vs fixed 1R | SOURCE-CONFLICT | Lesson explicitly gives AB=CD; official page gives default TP 1:1; reconciliation remains open. |
| TP-MP-02 | TP | TP1/R1 vs TP2/R2 | DISTINCT | First and second reward outcomes are distinct, but canonical exit mapping is unresolved. |
| TP-MP-03 | TP | candidate C vs fill price | UNDERDETERMINED | Fill price must not be silently equated with C. |

## Gate decision

**G375 PASS for research-layer execution; FROZEN GEOMETRY remains BLOCKED.**

The matrix confirms that several unresolved choices are outcome-changing, so they cannot be hidden inside implementation defaults. It also confirms two important non-promotions:

1. P-Gap cannot inherit the generic gap formula merely because a generic gap lesson provides an example geometry.
2. The official default 1:1 target cannot overwrite the lesson's explicit AB=CD concept without source reconciliation.

## Next action

Proceed to targeted SOURCE RESOLUTION (G372/G373/G374) for the unresolved variables that materially change outputs: P-Gap endpoints/overlap, A/B/C/D anchors and scale, pending-limit/fill semantics, exact SL boundary, TP mapping, and the scope of the 50% secondary entry.

No DEV, VAL, robustness, fresh-holdout, live signal, or production promotion is authorized by this artifact.
