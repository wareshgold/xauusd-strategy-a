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


## 12. Combined local validation — 32 synthetic tests passed

On 2026-11-16, the operator ran both research test modules together from the dedicated multi-account worktree using the project virtual environment:

- Worktree: `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-multi-account-foundation-20261116`
- Python: project venv at `D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\.venv\\Scripts\\python.exe`
- Test modules:
  - `tests/test_sp2l_account_isolation_contract_research.py`
  - `tests/test_sp2l_multi_account_recovery_contract_research.py`
- Import resolution: temporary test launcher inserted the worktree root into `sys.path`; no project source or test files were changed for this fix.
- Result: `EXIT_CODE=0`
- Result summary: `Ran 32 tests in 0.015s — OK`
- Breakdown: 12 account-isolation tests + 20 recovery/event/idempotency tests; all 32 passed.

This supersedes the earlier pending-validation statements in Sections 10 and 11 for these two modules. The validation remains limited to pure-Python synthetic contracts. It does not prove MT5 account identity extraction, terminal/process isolation, broker order/position linkage, durable journal semantics, real recovery, worker behavior, or any trading edge. No MT5 connection, broker action, account onboarding, or active V3.1 Runner modification was performed as part of this test run.


## 13. Broker-object ownership contract — 13 synthetic tests locally validated

After the 32-test combined validation, an offline-only broker-object ownership contract was added:

- `scripts/sp2l_broker_object_ownership_contract_research.py`
- `tests/test_sp2l_broker_object_ownership_contract_research.py`
- `docs/research/SP2L_BROKER_OBJECT_OWNERSHIP_RESEARCH_2026-11-16.md`
- `docs/research/SP2L_BROKER_OBJECT_OWNERSHIP_FIXTURES_2026-11-16.md`

Source-aligned design:
- Verify the supplied observed broker/server/opaque-login-reference against the expected account identity before inventory classification.
- Scope object keys by account key + object kind + ticket; ORDER and POSITION ticket namespaces remain distinct.
- Apply exact symbol + magic only within the already verified account session.
- Ignore well-formed objects outside the worker's symbol + magic scope; halt on malformed objects or conflicting duplicate object keys.
- Do not infer order.position_id / deal.position_id / position.ticket-or-identifier equivalence or implement order-to-position linkage.

The source review confirmed that the existing V3.1 recovery helper currently filters by symbol + magic and stores ticket integers, while the V3.1 wrapper queries inventory from its process-level MT5 session. The new contract is not integrated into V3.1 or any worker.

**Local validation (operator-run, 2026-11-16):**
- Branch: `research/multi-account-foundation-rfc-20261116`
- Dedicated multi-account worktree; clean Git status was checked before execution.
- Test module: `tests/test_sp2l_broker_object_ownership_contract_research.py`
- Result: `TEST_EXIT=0`, `RESULT=PASS`
- Result summary: `Ran 13 tests in 0.001s — OK`
- All 13 named synthetic tests passed.

This validates only the deterministic pure-Python ownership contract against synthetic observations. It does not validate MT5 account identity extraction, terminal/process isolation, actual broker inventory, order/deal/position linkage, partial fills, hedging/netting behavior, durable persistence, worker execution, or any trading edge. No MT5 connection, broker query/action, account activation, or active Runner modification occurred.

## 14. Combined multi-account synthetic validation — 45 tests passed

The operator's local validation evidence now covers three research test modules:
- Account identity isolation: 12/12 passed.
- Recovery, event isolation, and duplicate delivery: 20/20 passed.
- Broker-object ownership: 13/13 passed.

**Combined result:** 45/45 synthetic tests passed (32 + 13). This is offline contract/fixture validation only. It is not evidence of live or Demo MT5 isolation, broker behavior, production readiness, or a statistical trading edge. The active V3.1 Runner and all trading configuration remain outside scope and unchanged.


## 15. MT5 order/deal/position linkage — source research and synthetic fixtures authored

After the 45-test synthetic validation, official MQL5 documentation was reviewed and two offline research documents were added:

- `docs/research/SP2L_ORDER_DEAL_POSITION_LINKAGE_RESEARCH_2026-11-16.md`
- `docs/research/SP2L_ORDER_DEAL_POSITION_LINKAGE_FIXTURES_2026-11-16.md`

### Source-confirmed field distinctions

- `DEAL_ORDER` references an order ticket.
- `ORDER_POSITION_ID` and `DEAL_POSITION_ID` refer to a position identifier.
- `POSITION_IDENTIFIER` is documented as stable through the position lifecycle.
- `POSITION_TICKET` is a distinct current ticket and may change during server service operations; on netting reversal, MQL5 documents that the identifier remains while the ticket is replaced.
- Netting permits one position per symbol; hedging permits multiple same-symbol positions.
- Fill policy (FOK/IOC/RETURN), order state and volume fields affect partial execution interpretation.
- Trade transaction arrival order is not guaranteed; one request can produce multiple transactions.
- Close By exposes a separate opposite-position reference.

### Explicit unresolved items

- The Python Integration documentation describes `history_orders_get(position=...)` and `history_deals_get(position=...)` using “position ticket” wording while describing filters on `ORDER_POSITION_ID` and `DEAL_POSITION_ID`. The mapping to ticket versus identifier must be verified against the installed Python binding; no assumption is frozen.
- Partial-fill history representation may differ by filling policy, broker and execution mode. No one-order/one-deal cardinality rule is adopted.
- Broker-specific service operations, account margin mode and actual field availability have not been observed.
- The synthetic fixture plan is authored documentation, not executed tests; no additional test-pass count is claimed.

No linkage adapter or reconciliation algorithm was implemented. No MT5 connection, broker query/action, account activation, or active V3.1 Runner modification occurred. This work does not establish trading semantics or a statistical edge.

### Next gate

Convert only unambiguous source-confirmed field relationships into pure-Python fixtures/tests. Keep Python history-query parameter semantics and broker-specific partial-fill behavior unresolved until independently verified. A read-only mocked adapter remains the next possible engineering step; no live or Demo MT5 experiment is authorized by this snapshot.


## 16. MT5 linkage fact model and synthetic tests authored

A deliberately narrow pure-Python fact model and focused tests were added after the source research:

- `scripts/sp2l_order_deal_position_linkage_facts_research.py`
  - preserves `POSITION_TICKET` and `POSITION_IDENTIFIER` as separate fields;
  - preserves `ORDER_TICKET`, `ORDER_POSITION_ID`, `DEAL_TICKET`, `DEAL_ORDER`, and `DEAL_POSITION_ID` without aliasing;
  - retains order state, filling policy, volume fields, and Close By's opposite-position identifier as independent raw facts;
  - includes only a lifecycle comparison using `POSITION_IDENTIFIER`; no broker reconciliation or history query.
- `tests/test_sp2l_order_deal_position_linkage_facts_research.py`
  - 11 synthetic tests authored for explicit order/deal references, stable lifecycle identity, ticket replacement, netting reversal, same-symbol hedging positions, multiple deals, Close By, and raw partial-fill field preservation.

**Validation status:** authored on GitHub and pending local execution. These 11 tests are not counted in the previously operator-validated 45/45 result. No Python test runner was executed by this GitHub-only change. No broker, MT5 terminal, history API, active Runner, account, or order was accessed or modified.

The tests intentionally do not settle:
- Python `history_orders_get(position=...)` / `history_deals_get(position=...)` parameter meaning;
- broker-specific partial-fill history representation or cardinality;
- callback ordering, deduplication/replay semantics, or durable reconciliation;
- actual account margin mode, terminal/process isolation, or broker field availability.

The fixture document's implementation status is updated to distinguish authored tests from locally validated tests. The next gate is the operator-run focused test command in the dedicated multi-account worktree. Only after that result is reviewed should a read-only mocked history adapter be considered.


## 17. Python MT5 history position-filter source resolution

After the operator locally validated the 11 Order–Deal–Position fact-model tests (11/11, `TEST_EXIT=0`), official source research was extended to the Python history query parameter ambiguity.

Added:
- `docs/research/SP2L_PYTHON_HISTORY_POSITION_FILTER_SOURCE_RESOLUTION_2026-11-16.md`
- Commit: `08c81db9b19ab2a30f71231ef6bc336eb812cd06`

### Documentation-level conclusion

The official Python Integration pages describe:
- `history_orders_get(position=x)` as filtering `ORDER_POSITION_ID == x`;
- `history_deals_get(position=x)` as filtering `DEAL_POSITION_ID == x`.

The official MQL5 Position Properties reference defines `POSITION_IDENTIFIER` as the stable lifecycle identifier represented in those order/deal fields, while `POSITION_TICKET` is a separate current ticket that may change. The official MQL5 book's Python integration chapter explicitly calls the history argument a `POSITION_ID` and says it filters the corresponding `ORDER_POSITION_ID` / `DEAL_POSITION_ID` field.

**Research conclusion:** at documentation level, the intended Python history `position=` key is the position lifecycle identifier (`POSITION_IDENTIFIER`), not the current `POSITION_TICKET`. The Python Integration pages' “position ticket” wording is imprecise; the named filter fields and the official book clarify the intended semantic key.

### Remaining implementation boundary

- The installed MetaTrader5 Python package previously reported as `5.0.6180` has not been experimentally tested for this behavior.
- No compiled extension implementation was inspected.
- No query was issued to MT5 and no recorded result was tested with deliberately different `POSITION_TICKET` and `POSITION_IDENTIFIER` values.
- This source conclusion does not validate history completeness, broker behavior, or a reconciliation algorithm.

The 11 Order–Deal–Position fact-model tests were locally run by the operator:
- `TEST_EXIT=0`
- `Ran 11 tests`
- `OK`

This validates only the pure-Python synthetic fact model. It does not validate the Python package's history filter implementation.

### Next gate

Add synthetic fixture assertions for the documentation-derived mapping, then review a narrow read-only mocked history adapter contract. Keep package-specific compatibility, history completeness, partial-fill representation, and broker behavior explicitly unverified. No MT5 initialization, broker query/action, account activation, or active Runner modification occurred.


## 18. Documentation-derived Python history filter fixture added

Following the source resolution in Section 17, the research branch now contains an additional pure-Python fixture layer:

- `scripts/sp2l_order_deal_position_linkage_facts_research.py`
  - adds explicit predicates for the documented `ORDER_POSITION_ID` and `DEAL_POSITION_ID` history filter keys;
  - predicates are labeled as documentation-derived models, not calls to or verification of the compiled Python extension.
- `tests/test_sp2l_order_deal_position_linkage_facts_research.py`
  - adds three synthetic tests proving that, when `POSITION_TICKET=7001` and `POSITION_IDENTIFIER=9001`, the documented order/deal field filters match 9001 and do not match 7001 or an unrelated identifier.
- `docs/research/SP2L_ORDER_DEAL_POSITION_LINKAGE_FIXTURES_2026-11-16.md`
  - adds Fixture K and records the source boundary.

Commits:
- Model: `897a130faf319a36f592bb730ced4954db103a03`
- Tests: `f7e604eee94d06eea9723aa33766362c8caff8c2`
- Fixture documentation: `895782bbb2d6c39b92efb899c70f22682280fade`

**Validation status:** the original 11 tests were locally validated before these three tests were added. The updated module now contains 14 tests and is pending a fresh local run after pulling the latest branch. Do not count the three new tests as passed yet.

The new predicates model documented field semantics only. They do not query MT5, verify package version `5.0.6180`, establish history completeness, reconcile broker objects, or define partial-fill/execution behavior. No MT5 connection, broker action, account activation, or active Runner modification occurred.


## 19. Python history position-filter fixtures — 14/14 locally validated

After the operator pulled the research branch containing the three documentation-derived history-filter assertions, the updated focused test module was executed locally from the dedicated multi-account worktree on 2026-11-16:

- Test module: `tests.test_sp2l_order_deal_position_linkage_facts_research`
- Result: `TEST_EXIT=0`
- Result summary: `Ran 14 tests in 0.001s — OK`
- The 14 passing tests include the original 11 order/deal/position fact-model tests plus three synthetic assertions for the documented Python history `position=` filter mapping.

This supersedes Section 18's pending-local-run status for the 14-test module. The result validates only the pure-Python synthetic fact model and documentation-derived predicates. It does not experimentally verify the installed MetaTrader5 Python package (previously reported as 5.0.6180), compiled-extension behavior, MT5 history results/completeness, broker-specific partial fills, or any reconciliation algorithm.

No MT5 connection, broker query/action, account activation, order operation, or active V3.1 Runner modification occurred. The next possible offline step is to specify and test a read-only mocked history-adapter contract; any real package/terminal compatibility experiment remains outside scope unless separately authorized.


## 20. Read-only mocked history adapter contract authored

An offline-only injected-provider adapter and synthetic test module were added:

- `scripts/sp2l_read_only_history_adapter_research.py`
  - accepts an injected provider exposing the documented order/deal history method shape and `last_error()`;
  - passes the source-resolved position lifecycle identifier as the `position=` argument;
  - distinguishes non-empty tuple, valid empty tuple, `None` failure sentinel, provider exception, and unexpected result type;
  - preserves raw records and opaque API error payloads without rewriting or reconciling them;
  - has no MetaTrader5 import and performs no terminal, broker, filesystem, or Runner operations.
- `tests/test_sp2l_read_only_history_adapter_research.py`
  - 17 synthetic tests authored, including empty versus `None`, order/deal call separation, exact identifier argument, raw row preservation, error capture, invalid input rejection, missing provider method, and single-read `last_error()` behavior.
- `docs/research/SP2L_READ_ONLY_MOCKED_HISTORY_ADAPTER_RESEARCH_2026-11-16.md`
  - documents source alignment, result states, failure boundaries, non-goals, and validation limits.

**Validation status:** implementation and 17 tests are committed on this research branch but have not yet been executed in the operator's local environment. Do not report these tests as passing until the operator runs them. This is an injected fake-provider contract, not an installed-package compatibility test. It does not prove history completeness, broker behavior, account isolation, partial-fill semantics, or order/deal/position reconciliation.

No MetaTrader5 import, terminal initialization, broker query/action, account activation, order operation, or active V3.1 Runner modification was performed. The next step is a focused local synthetic test run from the dedicated multi-account worktree.
