# SP2L Assumption Dependency Evidence Inventory — 2026-09-19

## Purpose

Define exactly what can and cannot be attributed from the currently archived trade-level evidence, without inventing unresolved Strategy A geometry.

This document is a research/evidence artifact only. It does not promote any candidate rule to canonical Strategy A.

## Artifact reviewed

Available artifact:

`artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json`

Observed coverage:

- Week: 2026-09-14 through 2026-09-18 UTC
- Returned MT5 bars: 10,000
- First returned timestamp: 2026-09-09 18:12 UTC
- Last returned timestamp: 2026-09-18 23:57 UTC
- Signals: 38
- Wins: 27
- Losses: 10
- Ambiguous: 1
- Open/unresolved: 0
- Decisive win rate: 72.973%
- Total R: +17R
- Profit factor: 2.70
- Configuration: P-Gap 1.0, spike multiplier 1.5, max SL 10.0, TP 1.0R

The artifact contains trade-level Entry, SL, TP, risk, direction, signal time, outcome, exit time/price and reason.

## Dependency coverage

### 1. P-Gap

Status: **PARTIALLY ATTRIBUTABLE**

The trade artifact contains the final signal outcomes but not the full candle tuple and intermediate P-Gap measurements used to decide whether each candidate passed.

Therefore we can identify that the research runner used a P-Gap candidate implementation, but we cannot independently recompute or perturb P-Gap from this artifact alone.

Canonical status remains: **UNRESOLVED**.

### 2. Spike / body multiplier

Status: **PARTIALLY ATTRIBUTABLE**

The artifact records the resulting signals and the frozen multiplier value (1.5), but not the full four-candle OHLC evidence required to recompute the spike test independently.

A candle-level artifact is required for valid dependency analysis.

### 3. Relevant swing / SL anchor

Status: **NOT ATTRIBUTABLE FROM TRADE ARTIFACT ALONE**

The final SL price is present, but the candidate candle/swing structure from which it was derived is not.

Changing or testing swing selection from the trade artifact would require inference and would therefore violate the source-first boundary.

Canonical swing and exact SL anchor remain unresolved.

### 4. Trigger

Status: **PARTIALLY ATTRIBUTABLE**

Signal timestamps and directions are present, but the candle-level trigger relationship is not.

A valid trigger dependency test requires the relevant candles and their OHLC values.

Canonical trigger touch/index/fill semantics remain unresolved.

### 5. AB=CD

Status: **NOT ATTRIBUTABLE**

The archived trade rows do not contain A/B/C/D coordinates, endpoint semantics, or tolerance.

No AB=CD sensitivity test is justified from this artifact.

Canonical AB=CD remains unresolved.

### 6. Pending-order lifecycle / fill semantics

Status: **NOT ATTRIBUTABLE**

The trade artifact contains final signal/exit information but does not establish pending-order creation, refresh, cancellation, fill timestamp, or fill mechanics.

The F11 source audit remains authoritative: exact deletion predicate, refresh condition and fill semantics are unresolved.

### 7. TP / risk parameter

Status: **DIRECTLY OBSERVABLE, NOT CANONICAL**

The artifact records TP and risk and identifies TP = 1.0R for this research run.

This can support descriptive outcome analysis, but does not make 1.0R a canonical Strategy A parameter.

## What the current artifact can safely answer

- What happened to the 38 archived research signals.
- Which signals were WIN, LOSS or AMBIGUOUS.
- Aggregate descriptive performance for this research window.
- Descriptive relationship between observed trade outcomes and already-recorded trade fields.

## What it cannot safely answer

- Whether the source's exact P-Gap geometry is responsible for the edge.
- Whether another source-valid swing/SL interpretation would preserve the edge.
- Whether the exact source trigger semantics would preserve the edge.
- Whether AB=CD contributes to the observed edge.
- Whether pending-order lifecycle/fill semantics contribute to the observed edge.

Any attempt to answer those questions from aggregate trade rows alone would require reconstructing missing candle geometry or inventing a variant.

## Required next artifact

The next valid engineering step is a **candle-level, immutable research evidence artifact** for the same frozen historical window, containing:

- timestamp
- OHLC
- symbol/timeframe
- acquisition metadata
- exact source/revision identifier
- enough surrounding candles to reproduce each candidate signal
- mapping from signal to the candle indices used by the research runner

This artifact must be generated from the existing research path without changing the candidate rules.

It must not be used as a source-resolution mechanism.

## Gate impact

- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Assumption Dependency Audit: **EVIDENCE INVENTORY COMPLETE; ATTRIBUTION DATA INSUFFICIENT**
- Parameter Robustness: POSITIVE RESEARCH EVIDENCE
- Parameter Stability: INCONCLUSIVE
- Fresh Holdout: WAITING FOR ELIGIBLE POST-BOUNDARY DATA
- Production: BLOCKED
- Live Trading: DISABLED

## Non-inference rule

No unresolved source rule is promoted because the current research artifact performs well.

The next candle-level artifact is an evidence-acquisition step, not a strategy-definition step.
