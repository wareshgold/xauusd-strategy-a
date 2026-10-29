# V4 Phase 19 — Explicit MT5 Terminal Path & First Real Acquisition

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Branch/HEAD:** `research/strategy-v4-xauusd-20261028` / `592b77be`  
**Status:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`  
**Date:** 2026-10-28

## Changes made
- Modified `scripts/mt5_acquire_research_evidence_v1.py` to accept optional `--terminal-path` and call `mt5.initialize(path=...)` when supplied (backward compatible).
- Added test `test_terminal_path_argument_accepted` in `tests/test_mt5_acquire_research_evidence_v1.py`.

## Focused tests
- `tests/test_mt5_acquire_research_evidence_v1.py` → **5 passed**
- `tests/test_v4_research_fixtures.py` → **13 passed**
- `tests/test_v4_hash_key_regression.py` → **2 passed**  
**Total:** 20 passed

## First real acquisition (July only)
**Command executed:**
```bash
python scripts/mt5_acquire_research_evidence_v1.py \
  --start 2026-07-01T00:00:00Z --end 2026-08-01T00:00:00Z \
  --symbol XAUUSD.ecn --timeframe M1 \
  --evidence-root artifacts/mt5-research-evidence \
  --dataset-id xauusd_ecn_m1_2026_07_fresh_v1 \
  --terminal-path "C:\Program Files\Otet Group MT5 Terminal\terminal64.exe" \
  --note "Phase19 July fresh acquisition"
```

**Evidence directory (new):**  
`artifacts/mt5-research-evidence/xauusd_ecn_m1_2026_07_fresh_v1_20261029T055308Z/`

**Raw artifact:**  
`artifacts/mt5-research-evidence/xauusd_ecn_m1_2026_07_fresh_v1_20261029T055308Z/raw/xauusd_ecn_m1_2026_07_fresh_v1.csv`  
**Raw SHA256 (independent):** `f37d8242986862dc15f912f6c0d10b38aebb141d344bffcf9eaf5fe18926af87`  
**Manifest raw SHA256:** matches  
**Derived:** identity copy with hash matching raw (documented as transform)

**Verification:**
- Schema: `timestamp,open,high,low,close,tick_volume,spread,real_volume` ✓
- Lines/rows: 13266 lines / 13265 data rows ✓
- Requested: `2026-07-01T00:00:00Z` to `2026-08-01T00:00:00Z` (44641 bars)
- Actual: `2026-07-20T09:43:00Z` to `2026-07-31T23:57:00Z` (13265 bars)
- Gaps: 9 gaps (including large weekend gap 2943 min), chronological false, no invalid rows, no ordering anomalies recorded
- Audit status: `AUDITED_FAIL` (due to gaps/incomplete coverage)
- New directory created; prior evidence/datasets/manifests unchanged ✓

## Provenance note
This is a fresh retrieval from the specified terminal; it does **not** retroactively authenticate the existing July–September CSVs in `data/mt5-acquisition/` or their declared hashes. The old acquisition chain remains unresolved; historical session-calendar provenance remains UNVERIFIED. Raw export is immutable at the recorded path.

## August/September
Not acquired in this phase per instructions (review July first).

**Verdicts unchanged:** `SIGNAL_IDENTITY_NOT_ESTABLISHED / BLOCKED / NOT_PROVEN`
