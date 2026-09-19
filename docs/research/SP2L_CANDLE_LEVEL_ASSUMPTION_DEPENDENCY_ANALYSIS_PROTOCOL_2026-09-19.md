# SP2L Candle-Level Assumption Dependency Analysis Protocol — 2026-09-19

## Purpose

Define a deterministic, research-only analysis of the archived candle-level evidence for the 38 SP2L Strategy A research signals from 2026-09-14 through 2026-09-18 UTC.

This protocol measures evidence attribution and observability. It does not resolve source ambiguity, select canonical geometry, optimize parameters, or authorize execution.

## Frozen inputs

- Artifact: `artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json`
- Signal count: 38
- Symbol: XAUUSD.ecn
- Timeframe: M1
- Research configuration: P-Gap 1.0; Spike Multiplier 1.5; Max SL 10; TP 1.0R
- Mapping: 38/38 mapped; 0 missing; 0 insufficient context
- Candle index continuity: verified for the acquired artifact
- Outcome scan begins at the archived mapping's `outcome_scan_start_index`

## Analysis rules

For every mapped signal, preserve the supplied five-candle mapping exactly:

- A = `a_index`
- S = `s_index`
- correction = `correction_index`
- trigger = `trigger_index`
- signal = `signal_index`

Only relationships directly calculable from the supplied OHLC values are reported.

### P-Gap

Report candidate geometric measurements that can be computed from the mapped candles, but do not designate any measurement as the SP2L P-Gap formula. Do not infer indexing, mirror logic, wick/body semantics, threshold, or boundary semantics.

Status remains UNRESOLVED.

### Spike

Report descriptive candle body/range measurements and the configured multiplier as observed metadata. Do not infer or promote a canonical spike predicate.

### Trigger

Report directly observable High/Low relationships involving the mapped trigger/correction candles. Do not infer touch, wick, close, indexing precedence, pending/fill semantics, or canonical trigger predicate.

### SL / relevant swing

Report descriptive distances between archived Entry/SL and OHLC levels of the mapped context candles. This is evidence attribution only. Do not select a swing, candle, wick/body endpoint, buffer, or invalidation semantics as canonical.

### AB=CD

Return NOT_ATTRIBUTABLE_FROM_ARTIFACT because A/B/C/D coordinates, endpoint semantics, and tolerance are not fields in the candle-level evidence.

### Pending-order lifecycle / fill semantics

Return NOT_ATTRIBUTABLE_FROM_ARTIFACT because order creation, replacement, cancellation, fill event, and fill mechanics are not represented.

### TP / risk

Report the archived TP/risk relationship as directly observable metadata. Do not promote the configured value to canonical Strategy A.

## Required outputs

The implementation must produce:

1. immutable input artifact SHA-256;
2. signal-level evidence rows;
3. aggregate counts by attribution status;
4. explicit unresolved fields;
5. gap/context integrity status;
6. no optimized or promoted parameters;
7. a deterministic report hash.

## Gate rule

A positive or negative trade outcome must never change the canonical status of an unresolved source rule.

Expected gate impact after analysis:

- Assumption Dependency Audit: evidence attribution improved from insufficient to candle-level observable where fields permit;
- Frozen Geometry: remains BLOCKED;
- Production: remains BLOCKED;
- Live Trading: remains DISABLED.
