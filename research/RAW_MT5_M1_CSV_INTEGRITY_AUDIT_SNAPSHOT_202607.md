# Raw MT5 M1 CSV Integrity Audit Snapshot — July 2026

## Scope and authority

- Mode: `RESEARCH_RAW_MT5_M1_CSV_INTEGRITY_AUDIT`
- Status: `STRUCTURAL_INTEGRITY_PASS`
- Canonical: `false`
- Source artifacts modified: `false`
- This is a structural audit only. It does not certify data completeness, session-calendar applicability, trading readiness, or canonical Strategy A geometry.

## Audited artifact

- CSV: `data/mt5-acquisition/xauusd-ecn-m1-2026-07.csv`
- Manifest: `data/mt5-acquisition/xauusd-ecn-m1-2026-07.manifest.json`
- SHA-256: `482991df85c7143077ef3713c81f3c5ae14ae12311f6c03e3579f27f8048e34e`
- First timestamp: `2026-07-01T01:00:00Z`
- Last timestamp: `2026-07-31T23:57:00Z`

## Observed results

| Check | Result |
|---|---:|
| CSV data rows | 31,483 |
| Invalid rows | 0 |
| Duplicate timestamps | 0 |
| Out-of-order adjacent pairs | 0 |
| Timestamp gaps | 22 |
| Audit errors | 0 |
| Audit exit code | 0 |
| Manifest expected-active-bar count (diagnostic only) | 31,740 |
| Observed minus expected-active count (diagnostic only) | -257 |

All 22 timestamp gaps are reported as `UNCLASSIFIED_TIMESTAMP_GAP`. The report does not infer that these gaps are market closures or missing data. The manifest explicitly warns that the historical applicability of the session calendar is unverified; therefore the 257-bar difference is diagnostic only and must not be classified as a data defect or accepted as completeness proof without independent source/calendar evidence.

## Reproduction

```powershell
python .\scripts\sp2l_raw_m1_csv_integrity_audit.py `
  .\data\mt5-acquisition\xauusd-ecn-m1-2026-07.csv `
  --manifest .\data\mt5-acquisition\xauusd-ecn-m1-2026-07.manifest.json `
  --output .\artifacts\research\raw-m1-audit-2026-07-with-manifest.json
```

The audit JSON was generated locally and retained separately from the source CSV/manifest. Its exact generated timestamp is intentionally not treated as a stable fixture. The snapshot records the user-reported result, not an independently re-run audit by CI.

## Next evidence gate

Before using this month for validation or a fresh holdout, resolve the historical broker-session calendar against authoritative source evidence and classify the 22 observed gaps without assuming closure semantics. Preserve this report as a diagnostic; do not promote it to a completeness or strategy-readiness gate by itself.
