# MA Offline Observer — Frozen-Input Contract

Status: **RESEARCH-ONLY IMPLEMENTATION — OFFLINE_REPLAY ONLY**

Branch: `research/ma-filter-forward-week-20261114`

## Purpose and boundary

`scripts/research/ma_offline_observer.py` converts an explicitly supplied frozen JSON fixture/export into immutable observation JSONL plus a hash manifest.

It is deliberately **not** a candidate detector or a live shadow poller. It does not import the V3.1 Runner, import MetaTrader5, connect to a terminal, read Runner event/state files, query market data, infer decision timestamps, or issue trading/notification actions. Candidate IDs, trigger-bar timestamps, decision timestamps, monotonic timestamps, M1 bars, and bar boundaries are all supplied by the input producer.

Because this implementation consumes frozen inputs, its evidence mode is always `OFFLINE_REPLAY`. It must not be described as live Runner telemetry or as a forward research shadow stream.

## Input contract

The input is UTF-8 JSON with exactly these top-level fields:

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | string | Must equal `MA_OFFLINE_OBSERVER_INPUT_V1` |
| `run_id` | non-empty string | Caller-defined unique run label |
| `process_session_id` | non-empty string | Session identifier belonging to the supplied observations |
| `source_revision` | non-empty string | Exact research source revision used to prepare the fixture |
| `current_m1_bar_open_server_epoch` | integer | Explicit current M1 bar open in server epoch |
| `last_completed_m1_bar_open_server_epoch` | integer | Explicit last completed M1 bar open in server epoch |
| `last_completed_m1_bar_close_server_epoch` | integer | Explicit close boundary; no offset is inferred |
| `server_utc_offset_seconds` | integer or null | Null unless independently evidenced |
| `bars_snapshot` | array of bar objects | Ordered, exact snapshot; each bar has an integer `time` |
| `observations` | non-empty array | Supplied candidate-observation contexts |

Each observation has exactly:

- `candidate_id`: non-empty and unique within the run
- `poll_sequence`: non-negative integer, strictly increasing in input order
- `trigger_time_server_epoch`: integer trigger-bar open time; not decision time
- `decision_observed_at_utc`: explicit valid ISO-8601 UTC string ending in `Z`
- `decision_monotonic_ns`: explicit non-negative integer

The producer must capture the wall-clock and monotonic values at its own observation boundary. The offline observer never fills them from the current clock. A frozen fixture may use synthetic timestamps, but must remain labelled synthetic/offline.

## Run

From the repository root, with the project Python environment:

```powershell
& 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe' -m scripts.research.ma_offline_observer --input 'D:\path\to\frozen_fixture.json' --allowed-output-root 'D:\path\to\research_artifacts' --output-dir 'D:\path\to\research_artifacts\ma_observer\run-001'
```

The output directory must not already exist and must be a strict descendant of an existing `--allowed-output-root`. Its immediate parent must already exist; the observer does not create parent directories. The caller should point `--allowed-output-root` at a dedicated research-only artifact directory, never at the repository root, Runner workspace, or MT5 data directory. The observer creates only:

- `observations.jsonl` — one record per supplied observation, in input order
- `manifest.json` — schema versions, evidence mode, source revision, input/output SHA-256 hashes, record count, and alignment-status counts

If the target exists, the run fails closed. It never appends to or overwrites an earlier run. A partial output after an I/O failure is deliberately preserved for inspection rather than silently deleted.

## Hashing and determinism

- `input_sha256` hashes the exact original input bytes, including whitespace and key order.
- The bar snapshot hash is calculated by the existing record builder from the supplied ordered snapshot.
- JSONL records and manifest use canonical JSON serialization (sorted keys, compact separators, UTF-8) and LF record framing.
- Given byte-identical input, the output JSONL and manifest are byte-identical.
- Wall-clock and monotonic fields are supplied input values, not generated during replay.

## Fail-closed behavior

- Invalid UTF-8/JSON, unknown schema, missing/extra fields, duplicate candidate IDs, non-increasing poll sequences, malformed timestamps, and invalid monotonic values reject the run before output creation.
- Contradictory/missing bar boundaries are passed to the existing builder and retained as `UNRESOLVED`; records are not silently dropped.
- A null server offset remains null.
- No server-to-UTC conversion is attempted.
- No bars are sorted, synthesized, interpolated, or repaired.

## Verification

Run the focused tests:

```powershell
& 'D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe' -m unittest tests.test_ma_offline_observer -v
```

The tests cover deterministic end-to-end output, input/output hashes, unresolved-record preservation, duplicate IDs, poll-sequence validation, output-directory refusal, output file confinement, and static import/call checks for forbidden Runner/MT5/trading access.

## Explicit limitations / next gates

1. No candidate-detection algorithm is included. No detector semantics are invented or copied from the live Runner.
2. No live or read-only MT5 adapter is included.
3. No claim is made that the supplied observation context matches the live Runner's polling cadence or information set.
4. No MA period/type/filter is selected; no replay, fill, commission, spread, or intrabar semantics are resolved.
5. This deliverable is an offline evidence-packaging component only. A forward shadow collector and any live data adapter require separate design review and explicit approval.
