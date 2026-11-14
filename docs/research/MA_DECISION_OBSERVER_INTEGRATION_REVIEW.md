# MA Research — Isolated Observer Integration Review

Status: **DESIGN REVIEW — NO RUNNER OR MT5 INTEGRATION AUTHORIZED**

Branch: `research/ma-filter-forward-week-20261114`

## 1. Decision

The existing `ma_decision_observation.py` is suitable only as a pure record-building leaf function after its inputs have been captured by a caller. It is not an observer, poll loop, MT5 adapter, event writer, or integration with the V3.1 Runner.

The safe next implementation target is a **standalone research shadow observer** that consumes an explicitly supplied market-data snapshot and candidate observation context, writes research-only observation records, and has no order/trade-management capability.

The observer must not be described as capturing the live Runner's exact decision information set. A separate process has its own polling time, data snapshot, and observation boundary. Matching the live Runner's exact information set would require instrumentation at the live Runner's own candidate-observation boundary; that is outside this scope and would require separate explicit approval.

## 2. Three distinct evidence modes

| Mode | Source | What it can establish | Permitted status |
|---|---|---|---|
| Historical reconstruction | Existing JSONL/deals/M1 exports | Descriptive alignment proxies only where evidence supports them | Existing decision-time alignment remains `UNRESOLVED` |
| Offline replay observer | Frozen, hashed M1 snapshots plus pinned detector source | Deterministic behavior of the research observer over supplied snapshots | `OFFLINE_REPLAY`; never relabel as a live decision |
| Forward research shadow observer | Its own read-only market-data snapshots and poll loop | Timestamped observations made by the isolated shadow process | `RESEARCH_SHADOW`; not the production Runner's decision stream |

No evidence mode may backfill missing historical decision timestamps from `trigger_time`, file mtime, JSONL order, or deal time.

## 3. Proposed component boundary

The eventual isolated research package should have four separable layers:

1. **Snapshot input** — accepts a caller-supplied, ordered M1 snapshot and explicit server-time boundaries. Initial implementation should consume frozen fixture/export files. A live read-only market-data adapter is a separate later decision and must not connect to or inspect the active trading terminal without explicit approval.
2. **Candidate observer** — invokes only the pinned research copy of candidate-detection logic against that supplied snapshot. It records the observer's own poll sequence and observation time. It must not import the live Runner module as an executable module.
3. **Record builder** — calls `build_observation_record` with UTC wall-clock and monotonic timestamps captured immediately at the observation boundary, before hashing, logging, or other work. The builder does not infer timestamps or bar boundaries.
4. **Append-only evidence writer** — writes one JSONL record per observation to a new research output directory, with a manifest containing source revision, input snapshot hash, schema version, and output hash. It must refuse overwrite by default and must not write into the live Runner's event directory.

The initial deliverable should implement and test layers 2–4 using synthetic/frozen inputs only. It should not implement a terminal adapter.

## 4. Required record semantics

- `decision_observed_at_utc` and `decision_monotonic_ns` are captured by the caller at the observation boundary, not generated after processing the snapshot.
- `trigger_time_server_epoch` remains the triggering bar's server-epoch open time; it is never treated as the observation timestamp.
- The snapshot must include the current bar and identify the immediately preceding observed bar as the last completed bar. A time gap between those bars may be valid; an intervening snapshot bar that contradicts the declared completed bar is not.
- The completed-bar close boundary must be explicit and consistent with the verified source convention. No conversion from server time to UTC is allowed unless the offset is independently verified.
- Missing or contradictory boundaries yield `UNRESOLVED`; the writer must preserve that status and must not silently drop the record.
- The hash covers the exact ordered snapshot payload used by the observer. No sorting, synthetic bars, interpolation, or normalization that changes source values is allowed before hashing.
- A null server offset remains null. Server-epoch alignment within one snapshot does not require inventing a UTC offset.
- The observer's `candidate_id`, `process_session_id`, and `poll_sequence` identify its own observation only. It must not create fake order-attempt or order-result records.

## 5. Safety and isolation requirements

The research observer must have no code path to:

- `order_send`, order placement/cancellation, position modification/close, SL/TP changes, or account configuration;
- Telegram trade notifications or production signal publication;
- production BUY/SELL outputs or live configuration;
- the active Runner event directory or its state/recovery files.

Static and dynamic tests should verify:

- no import of MetaTrader5 or live Runner entrypoint in the observer package;
- no trading API symbols or calls in the observer package;
- no subprocess launch of the Runner or MT5 terminal;
- all file writes are confined to the designated research output directory;
- duplicate run IDs/output paths fail closed rather than overwrite;
- malformed records, missing boundaries, and invalid snapshots are retained as unresolved evidence or rejected explicitly according to the schema;
- deterministic replay of the same frozen input produces the same snapshot hash and equivalent record content, excluding explicitly captured wall-clock/monotonic fields.

A read-only data adapter, if ever proposed, must be reviewed separately. “Read-only” must be enforced by the adapter's exposed interface, not merely by convention.

## 6. Current code-review findings

The standalone builder review identified three validation gaps, now addressed in the research branch:

1. UTC validation previously checked only the trailing `Z`, without parsing the timestamp. A malformed string ending in `Z` could pass.
2. An empty timestamp string could fall back to a newly generated current timestamp instead of being rejected.
3. Snapshot validation previously accepted a declared completed bar that appeared earlier in the snapshot even when another bar intervened before the current bar.

Regression fixtures cover all three cases. The expanded local suite still needs to be rerun against the latest branch head before these changes are considered validated.

## 7. Acceptance gates before any forward shadow run

All of the following are required:

1. Builder and observer fixtures pass locally, including malformed/empty UTC, bar adjacency, gaps, missing offsets, out-of-order bars, and hash integrity.
2. A fake-input integration test proves the observer uses only the supplied snapshot and never queries MT5.
3. A filesystem test proves output confinement, append-only behavior, and no overwrite.
4. Static import/call-graph checks prove there is no trading API or live Runner import.
5. A synthetic end-to-end run emits a manifest and immutable JSONL evidence with reproducible hashes.
6. The resulting documentation explicitly labels the stream `RESEARCH_SHADOW` or `OFFLINE_REPLAY`, never production Runner telemetry.

Passing these gates authorizes only a research shadow data-collection experiment. It does not authorize MA filter selection, counterfactual replay, production integration, or trading decisions.

## 8. Explicit unresolved items

- Exact live Runner detection/poll timestamp remains unavailable in the audited historical event records.
- The isolated shadow process cannot claim to reproduce the exact live Runner polling schedule or information set.
- Any future live Runner instrumentation requires a separate scope and explicit approval.
- MT5 server offset and DST behavior must be independently evidenced before UTC/server-time conversion.
- Replay/fill/commission/spread/intrabar semantics remain separately blocked.
- No MA period, type, or filter has been selected or made canonical.

## 9. Implementation status — isolated offline recorder

The first implementation slice is now present:

- `scripts/research/ma_offline_observer.py` accepts only a frozen, explicit JSON input contract and emits `OFFLINE_REPLAY` JSONL plus a manifest.
- `tests/test_ma_offline_observer.py` provides synthetic end-to-end and isolation fixtures.
- `docs/research/MA_OFFLINE_OBSERVER_CONTRACT.md` defines the exact input schema, run command, output files, hashing, and limitations.

This is intentionally narrower than a candidate observer: it records caller-supplied candidate contexts and does not implement or invoke candidate-detection logic. That avoids silently choosing detector semantics. It also does not implement a forward poll loop, live data adapter, MT5 access, or Runner instrumentation.

The local test suite must be run after pulling the branch. Until that run is reviewed, implementation status is **CODED — LOCAL VALIDATION PENDING**. Even after tests pass, this component authorizes only offline evidence packaging, not a forward shadow run or any production integration.


## 10. Output-root confinement hardening — local validation pending

A follow-up review found that the first offline writer version created missing parent directories and did not enforce a caller-designated research output root. This was narrower than the intended filesystem-isolation guarantee. The research branch now requires an existing `allowed_output_root`, requires the output directory to be a strict descendant of that root, requires its immediate parent to exist already, and creates only the final output directory. The CLI exposes this as mandatory `--allowed-output-root`.

Regression tests now cover an output path outside the allowed root and refusal to create missing parent directories. The full focused test suite must be rerun locally after pulling the latest branch head. This hardening does not authorize use of a live adapter or processing of historical Runner events as exact decision-time observations.
