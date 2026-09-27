# SP2L Strategy A V2 Reconciliation Root-Cause Checkpoint — 2026-09-27

## Status

RESEARCH-ONLY / SOURCE-RESOLUTION CHECKPOINT.

No canonical Strategy A rule is promoted by this checkpoint.

## Reconciliation input

Artifact:
`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_SIGNAL_RECONCILIATION_20260927T054746Z.json`

Setup-level counts:

- V2: 139
- Source-aligned: 53
- Common: 53
- V2-only: 86
- Source-aligned-only: 0

The earlier two source-aligned-only cases were identified as artifacts of the old entry-key deduplication collector and are not used as geometry evidence.

## Full V2-only forensic classification

The segment-aware forensic run diagnosed all 86 V2-only cases.

Mutually exclusive root-cause classes:

| Root-cause class | Cases | Share |
|---|---:|---:|
| TRIGGER_TIMING_OR_ACCEPTANCE | 69 | 80.23% |
| TRIGGER_AND_TRIGGER_BODY_CONSTRAINT | 13 | 15.12% |
| SOURCE_RISK_CONSTRAINT | 4 | 4.65% |
| Total | 86 | 100.00% |

Immediate Source-aligned rejection checks are overlapping and therefore are not additive:

- trigger_lower_low: 34
- trigger_higher_high: 48
- spike_body_vs_trigger: 13
- source_risk_valid: 4

## Interpretation

The full forensic result localizes the observed V2-vs-source-aligned divergence primarily to trigger semantics/indexing:

- 69/86 V2-only cases are rejected by the Source-aligned immediate-trigger condition without the additional trigger-body constraint.
- 13/86 fail both trigger timing/acceptance and the Source-aligned trigger-body constraint.
- 4/86 are rejected by the Source-aligned risk constraint without the preceding trigger/body root cause.

This does NOT establish that the Source-aligned trigger interpretation is canonical or that the V2 trigger interpretation is canonical.

The official source evidence currently confirms the conceptual trigger direction (BUY retraces to the previous candle Low; SELL to the previous candle High), but exact trigger candle indexing and acceptance semantics remain unresolved.

## Gate decision

1. P-Gap formula is NOT resolved by this checkpoint.
2. Trigger indexing/acceptance remains unresolved.
3. No SL/fill/AB=CD rule is resolved by this checkpoint.
4. No optimization is authorized from these counts.
5. No canonical promotion is authorized.
6. No production BUY/SELL logic is changed.
7. The next research task is source-resolution/fixture work specifically for trigger indexing and acceptance semantics, using primary-source evidence where available.

## Reproducibility

Forensic artifact:
`artifacts/backtest-mt5-local/SP2L_STRATEGY_A_V2_RECONCILIATION_FORENSICS_20260927T055138Z.json`

Forensic tool commit:
`cea4f16f3c8e8f0bcdc402ad865aa86064f364e7`

The forensic implementation is segment-aware and diagnoses all V2-only cases by default.

## Boundary

This checkpoint is evidence about implementation divergence on the specified MT5 M1 window (2026-09-14 through 2026-09-25, session-filtered reconciliation). It is not evidence that either implementation represents the source-canonical Strategy A geometry.
