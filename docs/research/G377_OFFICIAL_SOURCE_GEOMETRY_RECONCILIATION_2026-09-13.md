# G377 — Official-Source Geometry Reconciliation

Date: 2026-09-13  
Gate: SOURCE RESOLUTION  
Canonical promotion: **BLOCKED**

## Objective
Reconcile the six remaining executable-geometry blockers using only authoritative SP2L source evidence already acquired. G376 machine fixtures are research-only and do not establish source meaning.

## Evidence hierarchy
1. Official SP2L source/page by Mohammad Ali Poursamadi.
2. SP2L source video/transcript and explicitly annotated source frames.
3. Existing source-resolution ledger (G353–G376).
4. Non-canonical hypotheses are discrimination aids only.

No chart-pixel inference, generic trading convention, third-party implementation, profitability result, or invented tolerance is promoted.

## Reconciliation matrix

| Dimension | Authoritative evidence | Status | Canonical rule? |
|---|---|---|---|
| P-Gap meaning | Source explicitly distinguishes P-Gap from E-Gap/Common-Gap; gap lesson identifies Pressure Gap as P-Gap. Valid Spike requires P-Gap. | PARTIALLY_RESOLVED | No |
| P-Gap executable endpoints / wick-body / overlap / minimum size | No authoritative source artifact found that explicitly defines these executable fields. Generic gap example is not promoted to P-Gap. | UNRESOLVED | No |
| A/B/C/D anchors | Source explicitly establishes AB=CD / Spike-2Leg and discusses Leg 1/Leg 2, including deeper/nested examples, but does not define universal OHLC anchor fields for A/B/C/D. | PARTIALLY_RESOLVED | No |
| Parent vs nested/deeper scale | Source demonstrates nested/deeper 2Leg structures, but no deterministic selection rule for canonical Strategy A scale was found. | UNRESOLVED | No |
| Pending-limit / trigger / fill | Source explicitly supports pending-limit entry during correction and distinguishes activation/trigger context, but exact limit-price formula and fill semantics are not fully defined. | PARTIALLY_RESOLVED | No |
| Structural SL boundary | Official source says SL is behind the candle from which Spike originated; exact wick/body/boundary interpretation is not explicitly fixed. | PARTIALLY_RESOLVED | No |
| TP / AB=CD mapping | Source supports AB=CD and lesson contains TP1/TP2/R1/R2 plus 2X/3X examples; official page separately states default TP 1:1. Exact reconciliation/mapping is absent. | CONTRADICTORY/UNRESOLVED | No |
| 50% secondary entry | Official page explicitly permits a secondary entry at 50% of entry-to-SL distance. Scope as core Strategy A versus optional add-on is not fully reconciled with the lesson. | PARTIALLY_RESOLVED | No |

## Findings

### 1. P-Gap
The semantic identity is now strong: P-Gap is the Pressure Gap concept used for a valid Spike. The source also teaches that location/context matters and distinguishes Pressure, Breakout, Exhaustion and Common gaps. This is sufficient for semantic labeling, but **not** for a deterministic candle/OHLC formula. The generic bullish gap geometry in the separate gap lesson must not be copied into P-Gap.

**Disposition:** keep P-Gap semantic concept frozen, executable geometry unresolved.

### 2. A/B/C/D and scale
AB=CD is source-confirmed as the 2Leg relationship. The source also shows parent/deeper/nested structures. However, the material does not provide an authoritative universal rule saying which candle extreme/body/close/structural event is A, B, C, or D, nor which scale must win when nested structures coexist.

**Disposition:** semantic relationship frozen; executable anchor/scale rules unresolved.

### 3. Entry and fill
The source supports correction-based pending-limit entry and shows that an order can be placed before the corrective activation/touch and later become activated/filled. The exact mathematical price of the limit and a complete trigger-versus-fill state machine are not source-defined.

**Disposition:** pending-limit mechanism is source-supported; exact executable fill semantics remain unresolved.

### 4. Stop
The official page states that the SL is placed behind the candle from which the Spike originated. That resolves the structural reference but not the exact OHLC boundary or any offset/tolerance.

**Disposition:** structural origin reference frozen; exact numerical boundary unresolved.

### 5. Target
The official page states a default 1:1 TP. The lesson separately documents AB=CD and TP1/TP2/R1/R2, including 2X/3X examples. These statements can coexist conceptually, but the source corpus does not define a deterministic mapping between them.

**Disposition:** do not select 1R, AB=CD, 2R, or 3R as the canonical Strategy A exit formula yet.

### 6. Secondary 50%
The official source explicitly describes a 50% secondary entry. It should therefore remain a documented source fact. But the current evidence does not establish that it is mandatory core-entry logic rather than an optional add-on.

**Disposition:** retain as optional/non-core until scope is explicitly resolved.

## Gate decision
**FROZEN GEOMETRY = BLOCKED.**

The semantic core is sufficiently resolved to continue research documentation, but the executable geometry required for deterministic Strategy A is not fully specified by authoritative source evidence. Therefore:

- No canonical Strategy A DEV backtest.
- No production implementation.
- No optimization of unresolved geometry.
- No promotion of G376 hypotheses.
- No conversion of generic gap geometry into P-Gap.
- No assumption that fill price equals C.
- No invented SL offset/tolerance.
- No fixed 2R/3R target rule.
- No generalized MA/session/candle-count filter.

## Next action
Proceed to the final source-resolution decision record (G378) using this matrix. If the primary source still does not contain the missing executable annotations, close the geometry cycle as blocked rather than inventing rules.
