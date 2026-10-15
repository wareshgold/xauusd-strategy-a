# MT5 Availability Integrity Gate — Invocation Contract

## Purpose

`scripts/sp2l_mt5_availability_integrity_gate.py` is a read-only, research-only
structural check for an already acquired MT5 availability manifest and its
referenced daily CSV and gaps JSON. It checks byte hashes and internal artifact
consistency. It does not connect to MT5, acquire bars, modify source artifacts,
infer a broker session calendar, or validate Strategy A trading rules.

## Windows / PowerShell invocation

From the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\sp2l_mt5_availability_integrity_gate.py data\mt5-session-availability\xauusd_ecn_m1_availability_matrix_2026Q1_Q3.manifest.json
$LASTEXITCODE
```

The script prints one JSON report to stdout. Exit code `0` means
`STRUCTURAL_INTEGRITY_PASS`; exit code `1` means
`STRUCTURAL_INTEGRITY_FAIL`. Preserve the complete JSON output as research
evidence if a run is recorded externally; do not rewrite the source manifest to
make a failing check pass.

## Interpretation boundary

A structural pass means only that the hashes and the checked internal counts
and timestamps agree. It does **not** establish market-session approval,
historical completeness, a cause for any gap, source readiness, canonical
Strategy A geometry, backtest eligibility, or production eligibility.

The report must retain:

- `canonical: false`
- `market_session_approval: "NOT_ESTABLISHED"`
- `research_interpretation: "RAW_AVAILABILITY_ONLY_NOT_SESSION_APPROVED"`
- `source_artifacts_modified: false`

A manifest with zero requested windows fails structural integrity, even when its daily and gap artifacts are empty and correctly hashed.

A failed check is a stop-and-review condition for this artifact; do not silently
skip the failure or infer a session cause from repeated timestamps.

## Factory integration boundary

At this stage, invoke the gate as a **standalone research audit**. It is not
wired into the Factory job lifecycle, Source Gate, Holdout gate, Forward Gate,
or production controls. Do not promote a structural pass into a general
readiness signal or add an automatic Factory transition based on it. Any future
integration must first define and test an explicit consumer contract that keeps
raw-availability integrity separate from session approval and dataset
completeness.

The gate is independent of the running Forward Test. Running it must not stop,
restart, reconfigure, or otherwise modify the Forward runner.
