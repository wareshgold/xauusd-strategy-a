# SP2L Forward/Backtest Reconciliation Harness — Deterministic Spec
## 2026-09-26

This is a research/forensic harness. It does not define or modify Strategy A geometry.

## Objective

For each historical candidate, reconcile:

`trigger_time -> detector_match -> session_eligibility -> theoretical_entry/SL/TP -> forward_visibility -> order_state -> fill/miss -> lifecycle`

The harness must fail closed: missing or ambiguous evidence is classified rather than guessed.

## Required evidence

### Historical side
- candidate trigger timestamp
- detector result / candidate identity
- entry
- SL
- TP
- session eligibility, if the historical run applies the research session filter

### Forward side
- candidate trigger timestamp or equivalent raw candle identity
- forward event timestamp
- visibility/observation event
- order state
- fill/miss state
- lifecycle START/STOP
- entry/SL/TP when available

If a field is absent, the harness must not infer it from neighboring records.

## Classification precedence

1. `DATA_GAP`
   - Required evidence is missing.
2. `TIMESTAMP_UNRESOLVED`
   - Candidate identity depends on a timestamp relationship that is not yet empirically resolved.
3. `SESSION_MISMATCH`
   - Historical eligibility and forward eligibility differ while geometry otherwise agrees.
4. `DETECTOR_MISMATCH`
   - Same candle identity is available, but detector output/entry/SL/TP differs.
5. `EXECUTION_MISMATCH`
   - Candidate and theoretical geometry agree, but order/fill/lifecycle behavior differs.
6. `MATCH`
   - Candidate, eligibility, theoretical levels, visibility, and execution/lifecycle evidence agree within explicitly supplied evidence.

No tolerance may be invented by the harness. Numeric equality must use exact source values unless a future research specification explicitly supplies a tolerance.

## Timestamp policy

Until an open-market probe establishes terminal timestamp semantics:
- do not apply a timezone offset;
- do not convert a raw MT5 timestamp by assumption;
- do not declare a candidate missing solely because wall-clock and candle time differ.

The harness may report `TIMESTAMP_UNRESOLVED`.

## Session policy

The historical research backtest currently has a London-open → New-York-close eligibility filter. The forward runner does not currently enforce the same filter.

This is an explicit research-universe difference. The harness must expose it as `SESSION_MISMATCH`; it must not silently modify either runner.

## Execution policy

The harness records research execution behavior only:
- pending-limit candidate,
- broker order acceptance/rejection,
- fill/miss,
- SL/TP outcome,
- lifecycle telemetry.

It must not infer a canonical fill rule from the observed outcome.

## Output schema

One row per historical candidate:

| Field | Meaning |
|---|---|
| candidate_id | deterministic identifier |
| trigger_time_raw | source trigger timestamp |
| trigger_time_interpreted | only when interpretation is established |
| detector_match | historical/forward detector agreement |
| session_historical | historical eligibility |
| session_forward | forward eligibility/observed state |
| entry_historical | theoretical historical entry |
| sl_historical | theoretical historical SL |
| tp_historical | theoretical historical TP |
| entry_forward | observed/reported forward entry |
| sl_forward | observed/reported forward SL |
| tp_forward | observed/reported forward TP |
| forward_visible | whether candidate was observed |
| order_state | observed order lifecycle state |
| fill_state | filled / missed / unknown |
| lifecycle_state | START/STOP coverage |
| classification | one of the six classifications above |
| evidence_refs | exact artifact references |
| notes | deterministic explanation |

## Required safeguards

- Research-only banner in generated reports.
- No production order generation.
- No detector mutation.
- No geometry mutation.
- No timestamp normalization.
- No fill-semantic mutation.
- No promotion of unresolved fields to canonical.

## Synthetic fixture policy

Synthetic fixtures may test the harness classification logic only. They must use explicit generic values and must not be used to invent or validate Strategy A geometry.

## First real execution

The harness should not be considered validated against live behavior until:
1. Monday open-market timestamp evidence exists.
2. Raw forward event logs are committed.
3. The same historical interval is replayed with the shared detector.
4. Candidate-by-candidate reconciliation is produced.
