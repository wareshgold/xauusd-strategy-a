# G378 — Source Closure Decision

Date: 2026-09-13  
Gate: SOURCE RESOLUTION → FROZEN GEOMETRY

## Decision

**FROZEN GEOMETRY = BLOCKED.**

The authoritative SP2L corpus is sufficient to freeze the semantic core, but it does not contain enough executable geometry to define a deterministic canonical Strategy A without invention.

## Resolved semantic facts

- SP2L is Spike → 2 Leg / AB=CD.
- A valid Spike is associated with P-Gap; the gap lesson establishes P-Gap as Pressure Gap.
- Pressure/Breakout/Exhaustion/Common gap concepts are distinct.
- The SP2L sequence is directional movement/Spike → Correction → Continuation.
- Correction and same-direction entry are source-supported.
- Pending-limit entry during correction is source-supported.
- Structural invalidation and a Spike-origin candle reference for SL are source-supported.
- AB=CD is source-supported.
- The official source states default TP 1:1.
- A 50% secondary entry is explicitly described by the official source.

## Executable geometry still unresolved

1. **P-Gap:** exact endpoints, wick/body treatment, overlap rule, and minimum-size condition.
2. **A/B/C/D:** universal anchor definitions and parent-vs-nested scale selection.
3. **Entry/fill:** exact pending-limit price and deterministic trigger/fill semantics.
4. **SL:** exact numerical boundary behind the Spike-origin candle; no offset may be invented.
5. **TP:** deterministic mapping between AB=CD, TP1/TP2/R1/R2 and the official default 1:1 is not specified.
6. **50% entry:** existence is source-confirmed, but mandatory core scope versus optional add-on is not fully reconciled.

## Promotion guard

The following remain prohibited from canonical Strategy A:

- generic gap formula promoted to P-Gap;
- third-party implementation geometry;
- chart-pixel inference;
- invented OHLC/wick/body selectors;
- C = fill price by assumption;
- invented SL offsets/tolerances;
- fixed 2R/3R target rule;
- generalized MA, session, or candle-count filters;
- optimization used to resolve source ambiguity.

## Gate consequences

Because executable geometry is incomplete:

- no canonical DEV backtest;
- no canonical VAL;
- no robustness/fresh-holdout promotion;
- no production/live signal engine based on unresolved hypotheses.

Research-only hypothesis fixtures may continue to be used as discrimination aids, but their outcomes cannot define source meaning.

## Re-entry condition

The project may enter **SYNTHETIC FIXTURES → FROZEN GEOMETRY** only after new authoritative source evidence resolves the executable blockers above, or after an explicit project-level decision to define a separate, clearly non-canonical experimental strategy.

This record therefore closes the current source-resolution cycle without manufacturing missing rules.
