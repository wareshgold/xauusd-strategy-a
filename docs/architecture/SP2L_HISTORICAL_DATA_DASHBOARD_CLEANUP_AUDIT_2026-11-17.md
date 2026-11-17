# SP2L Historical Data & Dashboard Cleanup Audit — 2026-11-17

## Status

- Scope: GitHub repository tree on `research/architecture-consolidation-plan-20261117`
- Inspected tree commit: `55e67c3f40237be47735efe05cb69d69a35783ea`
- Mode: static, read-only inventory
- No files deleted, moved, rewritten, or executed.
- No MT5 terminal, broker, runner, or Factory PC access was used.
- This is an initial inventory, not a completed dependency audit or deletion authorization.

## Repository inventory

The recursive Git tree contained 976 entries and was not truncated.

| Area | Tracked files | Tracked bytes | Approx. size |
|---|---:|---:|---:|
| `artifacts/` | 92 | 14,524,044 | 13.85 MiB |
| `data/` | 50 | 14,337,726 | 13.67 MiB |
| `docs/` | 285 | 1,072,192 | 1.02 MiB |
| `scripts/` | 174 | 1,206,715 | 1.15 MiB |
| `runtime/` | 5 | 14,253 | 0.01 MiB |

Counts and sizes describe tracked Git blobs on the inspected branch only. They do not describe local untracked files, ignored files, MT5 terminal data, or the Factory PC's actual disk usage.

## Large tracked data/artifact files

The following files are size outliers and should be reviewed for provenance and consumers, not deleted based on size:

| Path | Bytes | Initial disposition |
|---|---:|---|
| `artifacts/SP2L_candle_level_evidence_2026-09-14_2026-09-18.json` | 4,158,865 | KEEP pending evidence/provenance audit |
| `data/research/sp2l-feature-validation/observations.csv` | 3,675,460 | KEEP pending dataset-role and consumer audit |
| `artifacts/mt5_xauusd_m1_10000.json` | 2,466,817 | REVIEW identity/consumer; no deletion |
| `artifacts/mt5_xauusd_m1_fixed_10000.json` | 2,466,344 | REVIEW identity/consumer; no deletion |
| `data/mt5-acquisition/xauusd-ecn-m1-2026-07.csv` | 1,937,232 | KEEP with acquisition manifest pending lineage audit |
| `data/mt5-acquisition/xauusd-ecn-m1-2026-08.csv` | 1,781,865 | KEEP with acquisition manifest pending lineage audit |
| `data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv` | 1,773,482 | REVIEW overlap with monthly exports; preserve until equivalence is proven |
| `data/historical/xauusd-1min.json` | 1,575,969 | KEEP pending source/consumer audit |
| `data/historical/xauusd-5min.json` | 1,575,786 | KEEP pending source/consumer audit |
| `artifacts/xauusd-ecn-m1-recent-4week-2026-08-21_2026-09-17.csv` | 1,646,149 | KEEP pending provenance and consumer audit |
| `artifacts/forensic/runtime/SP2L_FORWARD_FORENSIC_TELEMETRY_20260926T055934Z.jsonl` | 1,523,865 | KEEP; raw forensic observation |

The monthly M1 exports, overlapping range exports, historical JSON datasets, and artifacts may represent different retrieval windows, schemas, session handling, or provenance. Similar names/date ranges are not proof of equivalence.

## Confirmed identical CSV content with distinct audit records

Two exact Git blob duplicates were found in `data/mt5-acquisition/`:

1. `xauusd-ecn-m1-session-aware-test-2026-09-17.csv`
2. `xauusd-ecn-m1-session-aware-test-2026-09-17-v2.csv`

Both paths have blob SHA `01bce4be72d164abdc656979323c5032624e82aa`. Their manifests have different dataset IDs and audit states: the first is `AUDITED_FAIL`; the v2 manifest is `AUDITED_PASS`. Both manifests point to the same underlying artifact SHA-256.

A second exact CSV duplicate pair:

1. `xauusd-ecn-m1-smoke-2026-09-17.csv`
2. `xauusd-ecn-m1-smoke-strict-2026-09-17.csv`

Both paths have blob SHA `009b968797c481a5a368b0b87f270dd161538011`. Their manifests have different dataset IDs and audit states: `AUDITED_PASS` versus `AUDITED_FAIL`.

Disposition: the content duplication is confirmed, but the audit records are not duplicates. Git object storage already deduplicates identical blob contents; deleting one path would save little repository object storage and could break manifest/path references. KEEP both paths and manifests until a path-reference and provenance migration is designed. Do not collapse the audit histories.

## Dashboard inventory

| File | Size | Observed role | Initial disposition |
|---|---:|---|---|
| `scripts/factory_dashboard.py` | 36,339 bytes | Factory telemetry dashboard, default port 8788; reads worker status and has isolated demo mode | KEEP / review entrypoint |
| `scripts/factory_starnet_world.py` | 11,795 bytes | StarNet world renderer, default port 8789; reads worker status and job event ledger | KEEP / optional renderer |
| `scripts/factory_demo.py` | 2,286 bytes | Writes separate demo telemetry file | KEEP isolated; never mix demo state with real telemetry |
| `scripts/live_dashboard.py` | 18,434 bytes | Legacy forward/live dashboard, default port 8790 | BLOCK deletion; audit current operational consumers and MT5 interaction |

Important safety finding: `scripts/live_dashboard.py` imports MetaTrader5 and its server-offset display helper may call `mt5.initialize()` and later `mt5.shutdown()` if it initialized the terminal. It must not be treated as a purely filesystem-only observer. This audit did not execute it.

The two Factory dashboards are not proven duplicates: one provides the main telemetry-backed dashboard and the other is a separate StarNet world renderer. The demo writer uses a separate status path. No renderer should be removed without checking launch scripts, runbooks, imports, and operator usage.

## Historical documentation

`docs/research/` contains 250 direct files plus an `archive/` directory on this branch. Many are dated checkpoints, source-resolution records, evidence inventories, forensic analyses, and validation reports. Age alone is not a deletion criterion. Initial disposition: KEEP; later create an index with superseded/current/historical/unresolved status. Preserve source evidence and decision history.

## Initial classification

- KEEP: raw source data, acquisition manifests, forensic telemetry, evidence artifacts, source-resolution and validation records.
- REVIEW: overlapping M1 exports, similarly named historical datasets, large generated matrices, old reports, dashboard launchers.
- ARCHIVE CANDIDATE: only generated summaries proven reproducible and no longer referenced; none are approved for archival in this report.
- DELETE CANDIDATE: none approved.
- UNKNOWN: local Factory PC files, ignored/untracked data, MT5 tester/history folders, and dashboard runtime state; not represented by GitHub tree.

## Remaining work before any cleanup

1. Scan all scripts, tests, workflows, package configuration, and runbooks for references to candidate datasets and dashboards.
2. Inspect manifests and dataset metadata for source, interval, schema, session calendar, content hashes, and intended roles.
3. Identify which historical exports are inputs to current reproducible workflows versus outputs retained only as evidence.
4. Audit local Factory PC paths read-only, including untracked/ignored files and sizes, without touching MT5 terminal/tester data or the active V3.1 runner.
5. Produce a per-path KEEP / ARCHIVE / REGENERATABLE / DELETE_CANDIDATE / UNKNOWN ledger with evidence for each decision.

## Safety boundary

No deletion, relocation, rewriting, compression, cleanup script, or live configuration change is authorized by this inventory. Any future deletion must be a separate, explicit, user-approved operation after dependency and evidence checks.
