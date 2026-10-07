# SP2L Factory Snapshot — 2026-10-07

## Status
- Branch: `research/sp2l-starnet-engine-integration-20261007`
- Scope: Holdout → Forward preparation boundary
- Strategy geometry: unchanged
- Production BUY/SELL authority: none
- Demo/live execution: not started from this Factory boundary

## Verified regression
Local regression suite:
- **45 passed in 1.26s**
- Command covered:
  - `tests/test_forward_preparation.py`
  - `tests/test_factory_forward_dry_run.py`
  - `tests/test_forward_orchestration.py`
  - `tests/test_mt5_reconciliation_adapter.py`
  - `tests/test_forward_runtime_adapter.py`
  - `tests/test_forward_runtime_bridge.py`
  - `tests/test_factory_forward_e2e_readiness.py`
  - `tests/test_forward_gate_factory.py`
  - `tests/test_forward_session_factory.py`
  - `tests/test_forward_session_lifecycle.py`

## Latest implementation boundary
- `HoldoutFactoryResult` carries the certified Holdout content SHA.
- `ForwardPreparation` validates the supplied Holdout SHA against that certified SHA.
- Registry dataset fingerprint is not treated as the raw artifact content SHA.
- Forward dataset identity remains distinct from Fresh Holdout identity.
- Frozen Strategy revision and no post-Holdout tuning remain enforced.
- No strategy geometry, entry/exit semantics, or production authorization was added.

## Latest implementation commits
- `c8f1dc784b8540f29cd814b0b7568de3a3693043`
- `27e9efa587b8f4053363069154f448dd06cd9e52`
- `4bd15a058d54d9b16948caad738672a70770243b`
- `3210a66059f0687fee83abb07d2f6bff29041f5e`

## Resume point
Next step: continue Factory integration from the frozen Holdout → Forward boundary. Do not start the formal one-day demo Forward until the Factory-bound session/orchestration path is complete and independently regression-tested.

## Research guardrails
SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → DEMO FORWARD → PRODUCTION.

Only source-confirmed rules may become canonical. Unresolved geometry remains unresolved.
