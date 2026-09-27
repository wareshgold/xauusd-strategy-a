# SP2L Candidate Readiness Infrastructure — 2026-09-27

## Purpose

The latest V2 replay result is useful as a research candidate:

- 222 detected signals
- 204 trades
- 127 wins
- 77 losses
- 62.2549% win rate
- +50R net
- PF 1.649
- max drawdown 6R

But it is NOT yet a validated Strategy A edge.

The corrected setup reconciliation found:

- V2 setups: 139
- source-aligned setups: 53
- common setups: 53
- V2-only setups: 86
- source-aligned-only: 0

The 86 extra V2 setups are therefore the immediate reproducibility problem. The infrastructure below treats that result as a candidate research track rather than repeatedly revisiting source wording.

## Operating principle

We do not need to solve every unresolved source detail before building the machinery.

Instead:

1. Keep each candidate interpretation isolated.
2. Give every candidate a stable ID and immutable configuration.
3. Run the same historical data through every candidate.
4. Store signal-level and trade-level records, not only aggregate statistics.
5. Compare candidates on identical bars, timestamps, costs, and exit conventions.
6. Prevent a candidate result from silently becoming canonical.
7. Only after a candidate survives reconciliation and untouched validation can it enter production-readiness review.

## Candidate tracks

### V2-CANDIDATE-001

Current candidate corresponding to the 2026-09-27 V2 replay.

Configuration is inherited from the existing V2 research contract:

- P-Gap price: 1.0
- Spike multiplier: 1.5
- Maximum base risk: 10.0
- TP: 1R
- Trigger research interpretation: current V2 implementation
- Second entry: disabled
- Filters: disabled
- Intrabar same-bar convention: SL first
- Canonical: false

This candidate must remain reproducible without modifying its historical definition.

## Required artifact layers

### 1. Dataset layer

Record:

- requested symbol
- resolved broker symbol
- timeframe
- start/end UTC
- raw bar count
- session-filtered bar count
- contiguous segments
- missing-data intervals
- data acquisition source
- MT5 terminal path/version when applicable

### 2. Candidate-definition layer

Record:

- candidate ID
- detector implementation identifier
- detector source SHA
- every numeric parameter
- trigger interpretation ID
- P-Gap interpretation ID
- SL interpretation ID
- fill interpretation ID
- filters
- session rules
- second-entry rules

No implicit defaults.

### 3. Signal layer

Every detected setup must have a stable record containing:

- candidate ID
- direction
- setup candle timestamps
- trigger timestamp
- entry price
- SL
- TP
- risk in price units
- rejection reason, if rejected
- source/candidate provenance

Aggregates are never sufficient evidence.

### 4. Execution layer

Every accepted signal must produce an execution record:

- order/position lifecycle
- intended entry
- actual fill
- fill timestamp
- spread/slippage when available
- SL/TP
- exit timestamp
- exit reason
- realized R
- ambiguity classification

Research replay and broker execution must remain separate fields.

### 5. Validation layer

Every candidate must pass, in order:

SOURCE/DEFINITION LOCK
→ DETERMINISTIC REPLAY
→ SETUP RECONCILIATION
→ SIGNAL-LEVEL RECONCILIATION
→ EXECUTION PARITY
→ UNTOUCHED VALIDATION
→ ROBUSTNESS/STABILITY
→ FRESH HOLDOUT
→ PRODUCTION READINESS

A failure blocks promotion; it does not get repaired by changing the historical result.

## Immediate engineering target

The next implementation should be a generic candidate-run harness around the existing V2 replay engine.

It must be able to:

- run a named candidate against the same MT5 M1 dataset;
- emit a manifest with candidate ID + code SHA + configuration;
- emit one JSONL/JSON record per signal/trade;
- preserve rejected candidates and rejection reasons;
- calculate aggregate metrics from the immutable trade records;
- compare two candidate runs by setup key and signal key;
- report added/removed/changed signals;
- never emit a production BUY/SELL decision.

## Promotion rule

The current 62.2549% / +50R result remains a RESEARCH CANDIDATE RESULT.

It must not be described as a proven edge until the candidate population is reproducible and survives untouched validation.

## Why this is the next step

This moves the project from repeatedly debating semantics to building the actual money-making research pipeline:

DATA → CANDIDATE → SIGNALS → EXECUTION → VALIDATION → HOLDOUT → PRODUCTION.

The unresolved source items remain explicit inputs to candidate IDs rather than becoming hidden assumptions.

Status: INFRASTRUCTURE SPEC READY FOR IMPLEMENTATION
