# V4 Phase 18 — Fresh Immutable MT5 Acquisition Attempt

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `3a7bcfea`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Date:** 2026-10-28

## State verification
- Branch/HEAD verified as above; protected files remain modified/unstaged as before.
- No existing datasets/manifests overwritten; no strategy/runners/configs/state changed.

## Script review (mt5_acquire_research_evidence_v1.py)
- Start/end parsed via `utc_parse` requiring UTC offset/Z; end must be > start.
- Uses `mt5.copy_rates_range(symbol, TIMEFRAME_M1, start, end)` with parsed UTC datetimes.
- Raw data written to `raw/<dataset_id>.csv` exactly as received (values converted via `repr(float(...))`); derived is identity copy with documented transform. Raw/derived hashes recorded separately.
- Manifest records symbol/timeframe/ranges (requested/actual), terminal/server, retrieval time, row count/schema, SHA256 (raw+derived), gaps/missing periods/ordering anomalies/duplicates, audit_status, limitations. Non-overwrite enforced by creating new timestamped dir and failing if exists.
- Fails closed on MT5 init/errors/unavailable terminal/server mismatch/zero bars.

**Interval semantics (as implemented):** passes start/end datetimes to `copy_rates_range` as parsed (minute-truncated). Exact inclusivity/exclusivity follow MT5 API behavior; the script records `requested_interval_utc` and `actual_first_utc/actual_last_utc` for verification. Treat as unverified without successful retrieval.

## Real acquisition attempt
**MT5 availability check:**
```python
import MetaTrader5 as mt5
mt5.initialize() -> False
mt5.terminal_info() -> None
mt5.account_info() -> None
mt5.shutdown()
```
**Result:** MT5 not initialized/available/authenticated in this environment. No real retrieval performed. No data files created by this phase. Existing evidence unchanged.

## Exact command to run (if MT5 available)
From repo root (`/d/Mirzaei/Private/1/xauusd-strategy-v4-research-20261028`):
```bash
python scripts/mt5_acquire_research_evidence_v1.py \
  --start 2026-07-01T00:00:00Z --end 2026-08-01T00:00:00Z \
  --symbol XAUUSD.ecn --timeframe M1 \
  --evidence-root artifacts/mt5-research-evidence \
  --dataset-id xauusd_ecn_m1_2026_07_fresh_v1 \
  --note "Phase18 fresh acquisition July"
```
Repeat for August (`2026-08-01T00:00:00Z` to `2026-09-01T00:00:00Z`, dataset-id `xauusd_ecn_m1_2026_08_fresh_v1`) and September (`2026-09-01T00:00:00Z` to `2026-09-18T00:00:00Z`, dataset-id `xauusd_ecn_m1_2026_09_fresh_v1`). Use unique dataset IDs; script will refuse to overwrite existing dirs.

**Prerequisites missing:** Authenticated/local MT5 terminal with history access for XAUUSD.ecn M1 and network/session availability. If login required, user must authenticate in terminal before running.

## Comparison status
No fresh acquisition performed, so no comparison artifacts to generate. Existing July–September remain as-is (hashes/rows as documented in Phase 16). Old acquisition chain remains **UNRESOLVED_PROVENANCE**; session calendar remains **UNVERIFIED**.

## Tests
- `pytest tests/test_mt5_acquire_research_evidence_v1.py -v` → 4 passed
- `pytest tests/test_v4_research_fixtures.py tests/test_v4_hash_key_regression.py -v` → 15 passed

## Commit/push
No new acquisition data committed (none retrieved). This report documents the attempt and procedure.
