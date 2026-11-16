# SP2L Multi-Account Foundation — Snapshot 2026-11-16

**Snapshot status:** recorded on GitHub  
**Research branch:** `research/multi-account-foundation-rfc-20261116`  
**Snapshot scope:** repository research state and operator-reported runtime state  
**Classification:** research-only, non-canonical, no live-account activation

## 1. Snapshot provenance

- Branch base: `research/v31-dashboard-local-monitor-20261104`
- Base branch HEAD at snapshot preparation: `bcf4e1bf97313a281dea04e7608b75d15108e3ec`
- Research branch parent before this snapshot: `cf3ab5066a5424b15ac1929f97ee979be683d386`
- Parent commit contains: `docs/SP2L_MULTI_ACCOUNT_FOUNDATION_RFC_RESEARCH_ONLY.md`
- Fati research source branch inspected: `research/fati-rr1-be5-no-tp-20261112`
- Fati source branch HEAD inspected: `f257694cab9d691b8b320a55ae3b7d012b2621a6`
- Active V3.1 Runner entrypoint source inspected from branch `fix/v31-explicit-server-offset-launch-20261116`, file blob: `c4ebfa074b542993f88541f357c72e1b1e4ea41c`
- Control Center branch: `feat/v31-monitor-control-center-20261116`; latest inspected monitor file blob: `bc4e6b8b1f42ce2d73d4b36e120dcf4aab57a096`
- Dashboard Control Center PR: #419, draft, not merged.

This is a source-reference snapshot, not a claim that the operator's local worktree is clean or synchronized. No local files or untracked runtime evidence were captured by this GitHub-only snapshot.

## 2. Operator-reported runtime state (2026-11-16)

- Active V3.1 Runner PIDs previously reported: `2212` and `12084`.
- Runner worktree: `D:\Mirzaei\Private\1\xauusd-strategy-a-v3-1-trailing-retry-20261103`.
- Runner identity: `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101`.
- Dashboard ports `8792`, `8793`, and `8794` were subsequently confirmed not listening after the operator requested all dashboards be stopped.
- No instruction was given to stop or restart the Runner; this work must not do so.
- Runtime state is operator-reported from the conversation, not independently queried during this GitHub snapshot.

## 3. Active Runner protection boundary

The currently active V3.1 Runner is out of scope for this development branch.

Do not:
- edit or replace its entrypoint, imported execution engine, trailing modules, runtime config, state, or event files;
- attach another MT5 Python IPC client to its terminal;
- stop, restart, or reconfigure its process;
- connect another account or submit orders.

All initial work is offline source audit, interface design, synthetic fixtures, and tests with broker boundaries mocked.

## 4. Fati source audit — findings and unresolved conflict

Inspected on `research/fati-rr1-be5-no-tp-20261112`:

- `scripts/fati_adapter_orchestration_research.py` — blob `d08bcc0186626319686aa9a2e6cd34235ddbefca`
- `scripts/fati_rr1_be5_no_tp_policy_research.py` — blob `e1c6848bea9cd5183c7cf36edfed4905e0628806`
- `scripts/fati_breakeven_policy_research.py` — blob `78daf96aa2aadb2e257c79e3c583f5febc51d292`
- `tests/test_fati_adapter_orchestration_research.py` — blob `1dbc8fbd1d8d328a28305ba74839f154d66e6084`
- `tests/test_fati_rr1_be5_no_tp_policy_research.py` — blob `ad2ba5c2f86bc23fac901a60d7e373691e744084`
- `tests/test_fati_breakeven_policy_research.py` — blob `1d53f94728d0b43832b8d36f5aad3d169bba7cbf`
- `docs/FATI_BREAKEVEN_OFFLINE_RESEARCH.md` — blob `fc7db5c5162abe583c07bb6c9b652e7c6955c4ab`

Observed implementation boundaries:
- Fati adapter is offline-only and has no MT5, network, broker, Telegram, or primary Runner imports.
- It validates an explicit account profile and approved signal, creates an inert initial-order intent with TP set to zero, and evaluates a supplied quote observation.
- The RR1/BE+5 helper proposes an SL change only; it does not execute a broker request or define quote sampling semantics.
- Broker confirmation/reconciliation is represented as pure state classification.
- The code inspected does not provide a complete independent Fati TP manager, account worker, MT5 terminal isolation, or production orchestration.

Important policy conflict:
- The inspected Fati research branch contains RR1 -> BE+5 behavior.
- The latest operator direction for the future Fati design is that Fati alone owns TP management, initial SL stays fixed, and the primary Runner's trailing logic is not reused.
- Whether any BE exception is permitted remains unresolved. Therefore RR1/BE+5 code must not be imported into a new worker or treated as approved policy until the operator explicitly resolves this conflict.
- Fati private Telegram routing remains limited to Pending Order and Order Filled; trade outcomes/results are excluded from that private route.

No conclusion about the correctness of the inspected Fati policy is made here.

## 5. Multi-account architecture direction

The research RFC proposes separate per-account workers and policy adapters, with independent:
- account identity fingerprint (no credentials in logs);
- terminal/process and broker-session ownership;
- symbol/contract profile;
- magic-number and order/position ownership;
- state, lock, recovery journal, event stream, and evidence manifest;
- risk limits, policy version, notification routing, and emergency stop.

A shared candidate population may be considered only as immutable input. Account-specific execution and management must remain isolated. The actual MT5 terminal/process topology is not yet proven and must be tested before implementation.

## 6. First development tasks

1. Build a read-only source map of current V3.1 runner boundaries: MT5 lifecycle, state schema, ownership keys, recovery, event emission, and imported execution functions.
2. Map Fati research code against the latest Fati constraints; do not reuse the unresolved BE path.
3. Define an account identity contract and per-account state namespace without connecting to MT5.
4. Add synthetic tests for account identity mismatch, cross-account state contamination, duplicate candidate delivery, duplicate order intent, corrupt/stale state, and ambiguous recovery.
5. Define an event/provenance contract for the read-only multi-account dashboard.
6. Only after offline tests pass, consider a no-order Demo isolation experiment with explicit operator approval.

## 7. Non-goals and canonical boundary

- No canonical SP2L geometry changes.
- No invented P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution semantics.
- No production BUY/SELL decisions by AI.
- No broker connection, order placement, SL/TP change, or live account onboarding.
- No claim of statistical edge from these architecture fixtures.

## 8. Required workflow

SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN INTERFACES → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION.

The active V3.1 Runner remains untouched throughout this snapshot and initial research development.


## 9. Initial implementation after snapshot capture

The following offline-only artifacts were added after the snapshot commit, on the same research branch:

- `scripts/sp2l_account_isolation_contract_research.py`
  - blob SHA: `a043d913cfa07a3082139ba847c17c89122c916f`
  - exact broker/server/opaque-login-reference match; fail-closed mismatch; no identity values echoed in exception text;
  - deterministic account-scoped state namespace and account-scoped candidate idempotency key;
  - no MT5, network, filesystem, Telegram, or Runner imports.
- `tests/test_sp2l_account_isolation_contract_research.py`
  - blob SHA: `03a9d8bba8c7764d625dbaa5b797406d3b799a9e`
  - 12 synthetic unit tests authored.
- `docs/research/SP2L_ACCOUNT_IDENTITY_ISOLATION_RESEARCH.md`
  - documents the contract and its limitations.

**Validation status:** GitHub file presence and source contents were re-read. The 12 tests have **not** been executed in the user's local Python environment; do not report them as passing. The next step is to pull this research branch into a separate worktree and run the focused test command. The active Runner remains outside the worktree and unchanged.


## 10. Local validation and V3.1 boundary audit update

On 2026-11-16, the user ran the account identity isolation test module locally from the dedicated multi-account worktree:

- Command target: `tests.test_sp2l_account_isolation_contract_research`
- Result: `TEST_EXIT=0`
- Result summary: `Ran 12 tests ... OK`
- All 12 synthetic identity/namespace tests passed. This validates only the pure-Python helper; it does not validate MT5 identity extraction, terminal/process isolation, order ownership, recovery, or worker behavior.

A read-only source-boundary audit was added:
- `docs/research/V31_MULTI_ACCOUNT_BOUNDARY_AUDIT_2026-11-16.md`
- Commit: `62b2bfe738968bf206b58c7f129e3488a1cf711d`

Key source findings:
- V3.1 and its imported runner share one process-level MT5 connection.
- Existing startup enforces DEMO mode but does not compare broker/server/login against an independently configured expected account identity.
- Symbol + magic scopes strategy ownership but does not prove account identity.
- State files and event streams are runner/worktree scoped, not account scoped.
- The base runner's state loader silently falls back to empty state on any load exception; that behavior must not be carried into a multi-account worker.
- Existing startup recovery correctly distinguishes failed inventory queries from valid empty snapshots, but it only classifies by symbol + magic.
- A shared OS runner lock coordinates worktrees; a future multi-account lock hierarchy must preserve duplicate-worker protection.
- The prior Fati adapter contains the unresolved RR1/BE+5 path and must not be reused under the latest fixed-initial-SL constraint.

No active Runner, MT5 terminal, account, order, or broker state was accessed or modified by this audit.


## 11. Recovery, event-isolation, and duplicate-delivery fixtures authored

Added three research-only artifacts:

- `scripts/sp2l_multi_account_recovery_contract_research.py`
  - commit: `88349fc1cfe2a13e3628644a297ee81be43fa7f5`
  - explicit state classifications: missing / valid / corrupt / incompatible;
  - fail-closed recovery disposition for unverified account identity, unavailable inventory, incomplete event journal, and ambiguous linkage;
  - missing state may bootstrap only against verified empty inventory and complete observations;
  - account-scoped event keys and per-account candidate-delivery classification;
  - pure Python; no MT5, filesystem, network, Telegram, or Runner imports.
- `tests/test_sp2l_multi_account_recovery_contract_research.py`
  - commit: `b9235501e5ab62237c498717c03ddcd55f8bb485`
  - 20 synthetic tests authored across state classification, recovery halts, event namespace isolation, and duplicate candidate delivery.
- `docs/research/SP2L_MULTI_ACCOUNT_RECOVERY_FIXTURES_2026-11-16.md`
  - commit: `b645b68b2d9662cfdbf1c6d05863e31d1b419412`
  - records fixture intent, limitations, and local validation command.

**Validation status:** these 20 tests are authored but not yet run locally. They must not be reported as passing until the operator supplies the local result. No active Runner or MT5 instance was accessed or changed.
