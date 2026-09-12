# G369 — Minimal-Pair Adversarial Fixture Design

Status: RESEARCH ONLY / canonical=false

## Objective
Expose whether unresolved geometry choices materially change deterministic outputs. Each pair changes one variable only.

### PGAP
- PG-MP-01: identical candles, alternate gap endpoint indexing.
- PG-MP-02: identical pressure context, wick-overlap vs body-separation.
- PG-MP-03: identical gap, weak-range context vs sustained-pressure context.
- PG-MP-04: breakout→FT→gap vs higher-structure→gap timing.

### ABCD
- AB-MP-01: same move, swing extreme vs candle boundary.
- AB-MP-02: same move, wick extreme vs body/close.
- AB-MP-03: same chart, shallow correction vs deep parent correction.
- AB-MP-04: nested leg vs parent leg.

### ENTRY/FILL
- EN-MP-01: corrective trigger occurs, later fill differs from trigger price.
- EN-MP-02: nominal geometric C is touched before/after trigger.
- EN-MP-03: pending limit remains unfilled while trigger condition occurs.

### SL
- SL-MP-01: origin candle wick extends beyond body.
- SL-MP-02: structural invalidation differs from origin extreme.

### TP
- TP-MP-01: AB=CD projection differs from fixed 1R target.
- TP-MP-02: first and second reward levels differ materially.
- TP-MP-03: same Leg1 with different candidate C/fill prices.

Every fixture records expected outputs for every applicable hypothesis and must not label any result canonical.