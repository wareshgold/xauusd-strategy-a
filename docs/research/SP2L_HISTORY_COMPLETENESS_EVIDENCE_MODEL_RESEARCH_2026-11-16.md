# SP2L History Completeness Evidence Model — Research Implementation (2026-11-16)

**Status:** offline research implementation; synthetic validation required  
**Canonical status:** non-canonical; no production caller  
**Runtime boundary:** no MetaTrader5 import, terminal access, broker calls, filesystem I/O, or Runner integration

## Artifacts

- `scripts/sp2l_history_completeness_evidence_research.py`
- `tests/test_sp2l_history_completeness_evidence_research.py`
- Protocol basis: `docs/research/SP2L_HISTORY_COMPLETENESS_EVIDENCE_PROTOCOL_RESEARCH_2026-11-16.md`

## Model

The model accepts already-captured, independent ORDERS and DEALS observations. Each query kind preserves:
- reported total count;
- returned tuple (including a valid empty tuple);
- opaque total-query error payload;
- opaque collection-query error payload.

The scope record requires:
- verified account identity reference;
- terminal/session reference and server name;
- exact from/to values;
- explicit time basis and its source;
- observation timestamp;
- observed package version and terminal build;
- SHA-256 evidence-manifest reference.

The model does not parse or convert timestamps, infer a server offset, call an API, or rewrite raw rows.

## Deterministic dispositions

- `INVALID_SCOPE`: required scope provenance is missing or invalid.
- `QUERY_FAILED`: a total or collection query failed, returned an invalid shape, used the wrong query kind, or supplied an invalid count.
- `COUNT_MISMATCH`: a successful total differs from the corresponding collection length.
- `OBSERVED_CONSISTENT_FOR_SCOPE`: both query kinds succeeded and both counts match.

A successful empty tuple is not an error. A missing collection (`None`) is a query failure.

## Hard boundary

`OBSERVED_CONSISTENT_FOR_SCOPE` is not `COMPLETENESS_PROVEN`. The helper `history_completeness_is_proven` deliberately always returns false: API-only count/collection observations cannot manufacture the independent completeness assertion required by the existing recovery gate.

This implementation is a deterministic evidence classifier, not an MT5 adapter and not a broker archive attestation. It does not establish atomicity across calls, lifecycle coverage, broker-side archive completeness, or order/deal reconciliation. No production recovery integration is permitted by this research artifact.

## Local validation command

```powershell
& 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe' -m unittest -v tests.test_sp2l_history_completeness_evidence_research
```
