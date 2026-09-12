# G292 — Target Selector Candidate Matrix

Date: 2026-09-12

## Source observations
The primary video target-construction sequence contains, in close succession:

1. a bullish `TP1 / TP2 / Entry / SL` schematic;
2. `Round level` discussion with examples including 2500, 3200, 3255 and 3250;
3. `250 point`;
4. `500 point`;
5. later `1000`.

The worked order-panel example earlier in the video contains actual TP prices and the target-side `1/2` reference construction.

## Candidate interpretations

| Candidate | Evidence | Status |
|---|---|---|
| TP1/TP2 are successive projected levels | explicit schematic | source-supported |
| target uses point-distance information | explicit `250 point`, `500 point`, `1000` annotations | source-supported concept |
| target uses Round Level information | explicit Round Level discussion | source-supported concept |
| TP1 = 250 points | visual proximity only | unresolved |
| TP2 = 500 points | visual proximity only | unresolved |
| Entry→TP2 = 1000 points | visual sequence only | unresolved |
| Round Level is terminal TP selector | no explicit selector statement | unresolved |
| Round Level overrides projection | no explicit rule | unresolved |
| `2` target reference is a round level | not demonstrated | unresolved |
| target `2` is AB=CD endpoint | no explicit anchor bridge | unresolved |
| target `2` is 2R | not demonstrated; worked example conflicts with simple 2R | unresolved / contradicted as a universal rule |

## Important cross-example result
The worked order panel provides a useful falsification check against a universal `TP = Entry ± 2R` rule. At least one observed order state has Entry 3223.84, SL 3235.50 and TP 3213.33; this gives risk 11.66 and Entry→TP 10.51, not 23.32.

This does **not** identify the correct target formula. It only rejects that simple universal candidate for the observed state.

## Selector status
`TARGET_SELECTOR = UNKNOWN`

No deterministic selector may currently choose among:
- Leg/AB=CD projection;
- point-distance targets;
- Round Level targets;
- or a combination of these.

The research engine may retain these as explicitly named hypotheses, but production must fail closed when target geometry is unresolved.
