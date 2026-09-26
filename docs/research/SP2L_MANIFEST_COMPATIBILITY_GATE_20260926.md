# SP2L Manifest Compatibility Gate — 2026-09-26

## Purpose

All current MT5 research replay/forensic runners now fail closed unless they match the source-aligned research manifest.

## Gated runners

- `scripts/run_sp2l_mt5_local_multi_symbol_backtest.py`
- `scripts/run-author-replica-mt5-api.py`
- `scripts/run_sp2l_forward_forensic_telemetry.py`

## Gate checks

1. Manifest exists at `docs/research/SP2L_RESEARCH_RULE_MANIFEST_20260926.md`.
2. The manifest contains the unresolved-geometry markers.
3. The manifest references source-evidence checkpoint `3778152049ec374830769007ed91f84b301187bb`.
4. Detector revision is `AR-20260926-01`.
5. Candidate parameters exactly match the manifest-compatible Author-Replica candidate:
   - P-Gap price = 1.0
   - Spike multiplier = 1.5
   - Max SL distance = 10.0
   - TP R = 1.0

The gate is intentionally a **research compatibility gate**, not a canonical Strategy A gate.

## Artifact traceability

Successful runs embed the gate result and candidate configuration in their JSON/JSONL metadata.

A parameter mismatch or missing/stale manifest raises an error before the MT5 research run proceeds.

## Canonical status

- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF

No source-unresolved field was promoted by this change.
