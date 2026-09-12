# G290 — Worked Trade Target Bridge Audit

Date: 2026-09-12

## Objective
Test whether the worked trade/order-panel sequence in the primary SP2L video provides a unique numerical bridge from the target schematic to executable TP values.

## Source slice reviewed
Primary SP2L video, approximately 21:20–24:20.

The worked example shows a bearish chart with the recurring measurement labels `0.0`, `2x`, `E`, `1`, and `2`, plus order-panel rows containing Entry, S/L and T/P prices.

## Observed order-panel states

| State | Entry | SL | TP | Entry→TP | Risk | 2R from Entry |
|---|---:|---:|---:|---:|---:|---:|
| A | 3229.08 | 3237.12 | 3213.44 | 15.64 | 8.04 | 16.08 |
| B | 3223.84 | 3235.50 | 3213.33 | 10.51 | 11.66 | 23.32 |
| C | 3228.88 | 3235.50 | 3213.45 | 15.43 | 6.62 | 13.24 |

The same target region remains visually associated with the `2` reference level while Entries and SL values differ across order states.

## Findings

1. The order panel establishes that real executable TP prices were used in the worked example.
2. The TP values are close to the same target region across different Entry/SL states.
3. State B is incompatible with a simple `TP = Entry ± 2R` rule: 2R would be 23.32 price units from Entry, while observed Entry→TP is 10.51.
4. States A and C happen to be numerically closer to 2R, but this coincidence cannot establish an R-multiple rule.
5. The recurring chart labels `1` and `2` are therefore not safely interpretable as `1R` and `2R` from this worked example alone.

## Canonical decision
`WORKED_TRADE_NUMERIC_BRIDGE = PARTIAL`

The worked example provides strong evidence that the target is constructed independently of a naive fixed-R formula, but it does not uniquely identify the construction equation or anchor points.

## Prohibited inference
Do not promote any of the following to production:
- `TP = 2R`;
- `TP = Entry ± 2R`;
- `2 = 2R`;
- `2 = TP` merely because the TP lies near the plotted `2` level;
- `TP = AB=CD endpoint`;
- `Entry = C`;
- any specific point/tick conversion;
- any spread/rounding explanation for the small price differences.

## Gate implication
The target geometry remains unresolved. The next source-resolution test is to map the `1/2` measurement ladder to the source's explicit Leg/AB=CD construction, rather than treating the order-panel TP as proof of a formula.
