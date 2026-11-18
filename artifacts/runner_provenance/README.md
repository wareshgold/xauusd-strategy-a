# Runner / Position Provenance — Research Design

Status: research-only V3.1 integration implemented on branch research/v31-runner-provenance-integration-20261118; not merged, not deployed, and not enabled in the active Runner.

## Purpose

Make every future runner execution and broker position traceable to the exact
runner version, Git commit, and immutable configuration snapshot that created it.
This is an observability/evidence feature only. It does not define SP2L geometry,
order semantics, fills, risk rules, or trading decisions.

## Identity model

- `runner_id`: stable logical runner family (e.g. `SP2L_V3_1_XAUUSD`).
- `runner_version`: explicit human-readable build/version label.
- `run_id`: unique 128-bit ID generated once per process execution.
- `git_commit`: exact source commit; must be captured from the running build.
- `config_snapshot`: complete explicit, JSON-safe effective configuration.
- `config_hash_sha256`: SHA-256 over canonical JSON (sorted keys, compact UTF-8).
- `config_id`: readable label derived from the first 12 hash hex characters.

The configuration snapshot must contain effective values after all environment
overrides and wrapper assignments. It must not contain passwords, tokens,
account credentials, or other secrets. A config hash is only meaningful if the
snapshot is complete and sourced from the actual runtime values.

## Position linkage

A `POSITION_LINKED` evidence event joins:
- run identity: run_id, runner_id, runner_version, git_commit;
- config identity: config_id and config_hash_sha256;
- observed broker identifiers: position_id, order_ticket, deal_ticket;
- symbol and magic;
- broker comment as an explicitly untrusted correlation hint.

The short MT5 comment token is `S2L:<run-id-prefix>:<config-hash-prefix>`.
It is not authoritative: brokers can truncate, rewrite, or omit comments.
The append-only local evidence log is the primary link source.

## Evidence integrity

- Run manifest is create-once; an existing path is never overwritten.
- JSONL events are append-only and hash-chained with sequence numbers.
- Startup verification fails closed on malformed, truncated, reordered, or
  modified prior events.
- The prototype assumes one writer process per event log. Multi-process use
  requires an explicit lock/coordination design before integration.
- Files should be retained with the run artifacts and included in a SHA-256
  evidence manifest at run completion.

## Integration gates — NOT YET APPROVED

1. Confirm the actual effective config fields for each runner wrapper.
2. Capture the exact Git commit from build metadata; do not silently use
   `unknown` or the repository's current HEAD if it differs from running code.
3. Write the immutable run manifest and `RUNNER_STARTED` before any order path.
4. Link broker position identifiers only after they are observed from MT5
   acknowledgements/history; do not infer position_id from order_ticket.
5. Add recovery/reconciliation for partial fills, multiple deals per position,
   pending orders, netting/hedging behavior, and broker comment loss.
6. Add unit, mutation, and synthetic MT5-response fixtures.
7. Review event privacy, storage location, retention, and failure policy.
8. Only then propose a separate integration PR. No change to active V3.1 runner.

## Current limitations

- No MT5 dependency or terminal connection.
- No order send/modify/cancel calls.
- No live Runner imports.
- The helper accepts a caller-supplied config snapshot; it cannot prove the
  caller supplied every effective setting.
- The hash chain detects accidental/ordinary tampering but is not a digital
  signature against an attacker able to rewrite the entire file and recompute it.
- Broker history may not expose every historical SL/TP request/response. This
  provenance feature does not solve missing broker-side records.


## V3.1 XAUUSD integration mapping (source inspection, not connected)

Inspected source files at the current research base:
- `scripts/run_sp2l_v3_1_xauusd_forward_test.py`
- `scripts/sp2l_v3_1_rr4_act40_config.py`
- `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py`

The wrapper delegates to the generic runner and monkey-patches selected functions.
The following values are source-confirmed effective V3.1 settings at those source
revisions; runtime environment and broker-resolved values must still be captured
at process startup, not assumed from this table.

| Field | V3.1 source value | Provenance |
|---|---:|---|
| runner_id | `SP2L_V3_1_XAUUSD` | stable proposed identity |
| runner_version | `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101` | `cfg.VERSION` |
| base symbol | `XAUUSD` | wrapper/config |
| timeframe | `M1` | generic runner |
| P-Gap price | `1.0` | `cfg.P_GAP_PRICE` |
| spike multiplier | `1.5` | `cfg.SPIKE_MULTIPLIER` |
| max SL distance | `10.0` | `cfg.MAX_SL_DISTANCE` |
| TP multiple | `4.0R` | `cfg.TP_R` |
| trailing distance | `0.40` price | `TRAIL_PIPS=4.0`, `XAU_PIP_SIZE_PRICE=0.1` |
| activation threshold | `0.40` price | same `TRAIL_DISTANCE_PRICE` used by activation check |
| order mode | `PENDING_LIMIT_RESEARCH` | `cfg.ORDER_MODE` |
| SL anchor label | `SPIKE_CANDLE_EXTREME_RESEARCH` | `cfg.SL_ANCHOR` |
| pending TTL | `30.0` minutes | `cfg.PENDING_TTL_MINUTES` |
| session policy | all market hours | wrapper overrides session function |
| base volume | `0.01` | `cfg.VOLUME` |
| magic base | `26092300` | wrapper |
| XAU slot magic | `26092301` | generic rule: base + index + 1 |
| execution flags | defaults set to `true/true` | wrapper `setdefault`; DEMO-only guard remains enforced |

Important effective-value distinctions:
- The generic runner's default London/New York session window is overridden by
  the V3.1 wrapper's all-market-hours function. Hash the effective override,
  not the unused generic defaults.
- `POLL_SECONDS`, `SP2L_PENDING_SERVER_OFFSET_HOURS`, terminal path, and
  broker-resolved symbol metadata are runtime values. Capture their actual
  effective values. The pinned server offset must never be invented or omitted
  from the runtime evidence if execution depends on it.
- The resolved symbol (for example `XAUUSD.ecn`), point, digits, pip size and
  method, trade mode, and volume min/max/step come from MT5 at runtime.
- Do not include credentials, Telegram tokens, passwords, or other secrets in
  the config snapshot. Account login/server may be stored separately in a
  restricted run-context record if the operator approves.

### Safe hook locations

1. After MT5 demo guard, symbol resolution, singleton runner lock, and startup
   recovery have succeeded — but before the existing `START` event and before
   entering the polling loop — create the per-run manifest and
   `RUNNER_STARTED` event. Any manifest/log failure aborts before order flow.
2. Before `execute_candidate`, append and fsync an `ORDER_INTENT` event
   containing run_id, signal_id, symbol, direction, magic and theoretical
   levels. If this write fails, do not call the execution function.
3. After the gateway result, append `ORDER_RESULT` with returned order/deal
   tickets and the broker result. If evidence persistence fails after broker
   acknowledgement, stop the runner and require reconciliation; do not silently
   continue as if the order were fully evidenced.
4. In the history-deal observer, use the broker's actual `deal.position_id`,
   `deal.order`, and `deal.ticket` to link entry deals. Never assume an order
   ticket is a position ID. Partial fills may create multiple entry deals for
   one position; preserve every deal/order relationship.
5. Preserve the existing `signal_orders` and `position_orders` correlations
   as supporting evidence, but do not infer a missing broker identifier.

### Restart and legacy-position rule

A process restart creates a new run_id, but an already-open position retains
the provenance of the run that opened it. Therefore:
- Keep a durable index from order/deal/position identifiers to the original
  run_id and manifest.
- On restart, recover links from the provenance index and broker history.
- Do not re-label an older position with the newly started run_id merely
  because it shares the same magic number.
- If an existing position predates instrumentation or cannot be reconciled,
  label it `PRE_PROVENANCE_UNATTRIBUTED` / `UNRESOLVED_LINK`; never guess.
- Record later management activity under the managing run separately from
  entry provenance. Do not overwrite the original entry config identity.

### Remaining integration blockers

- The current V3.1 runner source does not yet import or call this module.
- The effective Git commit and dirty-worktree state are not currently captured
  by the wrapper. Integration must prove the exact executing source revision;
  a dirty or unknown build must be blocked from claiming a clean commit identity.
- Position/deal reconciliation across restart, partial fills, and broker history
  needs synthetic fixtures before wiring.
- The event log currently assumes one writer. Use a unique per-run file and the
  existing singleton lock, or implement an explicit cross-process lock before
  any multi-writer deployment.
- The MT5 comment token is not integrated. Inspect the gateway request builder
  first; adding a comment is optional and must not alter execution behavior.
- No production or live-account use is authorized by this design.


## V3.1 integration implementation — research branch

The V3.1 wrapper now wires the helper into its own lifecycle. The generic
author-replica runner and the strategy/config geometry are not modified.

### Startup boundary

After the existing DEMO guard, symbol resolution, singleton lock, state load,
and V3.1 broker-inventory recovery have succeeded — and before the generic
runner emits START or enters its poll loop — the wrapper:

1. Reads the exact Git HEAD from the repository containing the executing
   runner and requires a clean worktree (including untracked files). It refuses
   to claim a clean commit identity if source differs from HEAD.
2. Captures the effective V3.1 strategy settings, runtime environment values,
   resolved MT5 symbol names and symbol metadata, selected terminal path,
   poll interval, pinned server offset, execution flags, MT5 version, and
   account trade mode. Credentials, account login, server identity, and
   Telegram secrets are deliberately excluded.
3. Creates a unique run directory and create-once manifest.json.
4. Verifies the existing shared event chain and appends/fsyncs RUNNER_STARTED.

Any failure in these steps aborts startup before the entry loop.

### Order evidence and fail-closed behavior

- ORDER_INTENT is appended and fsynced immediately before the existing
  execute_candidate gateway call. Failure blocks the order.
- ORDER_RESULT records the returned gateway result and broker order/deal
  tickets. If the gateway raises, the wrapper records an unknown outcome and
  stops because broker acknowledgement may be ambiguous.
- If result persistence fails after the gateway returns, the process stops
  and requires broker reconciliation. It does not continue as if the order
  were evidenced.
- No MT5 comment token was added; gateway request construction and execution
  semantics remain unchanged.

### Position and restart attribution

The V3.1 tracked-deal observer links only an observed DEAL_ENTRY_IN deal
whose timestamp is strictly later than the current process start, whose magic
matches the V3.1 symbol slot, and whose actual position_id is positive.
Every partial-fill deal is preserved as its own POSITION_LINKED event; the
broker order ticket is never substituted for a position ID.

The shared artifacts/forward-test/runner_provenance/events.jsonl log preserves
links across restarts. A restarted process does not relabel pre-existing
positions as belonging to its new run. Existing positions whose original
entry predates instrumentation remain unattributed unless independently
reconciled from retained evidence.

### Evidence locations

- Per-run manifest:
  artifacts/forward-test/runner_provenance/runs/<run_id>/manifest.json
- Shared append-only event chain:
  artifacts/forward-test/runner_provenance/events.jsonl

The existing singleton runner lock is the single-writer guard for the shared
event chain. Each append is flushed and fsynced. Startup verifies the full
prior chain before extending it. The chain is tamper-evident, not a digital
signature.

### Validation and deployment boundary

This branch adds deterministic tests for current-run entry eligibility,
restart attribution, and multiple partial fills. CI compiles the V3.1 wrapper
and provenance modules and runs the isolated provenance unit suite.

This remains a research integration proposal. It has not been merged or
deployed, does not change the active V3.1 process, and is not authorization
for live-account use. Before any operator deployment, verify the target
worktree is clean, the exact checked-out commit matches the intended PR head,
and the evidence directory is writable and retained. Do not retrofit
pre-instrumentation positions by guessing.
