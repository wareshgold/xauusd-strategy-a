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


## 21. Read-only mocked history adapter — 17/17 locally validated

After the operator pulled branch `research/multi-account-foundation-rfc-20261116` at HEAD `be71b936fba4d7dc6c4a9d117d4035c5c29c3ef8`, the focused adapter test module was executed locally from the dedicated multi-account worktree:

- Test module: `tests.test_sp2l_read_only_history_adapter_research`
- Result: `TEST_EXIT=0`
- Result summary: `Ran 17 tests in 0.001s — OK`
- All 17 named synthetic tests passed, covering exact position-identifier arguments, separate order/deal calls, empty tuple versus `None`, provider exceptions, `last_error()` handling, invalid identifiers, unexpected result types, immutable tuple container, and raw-row preservation without filtering/reconciliation.

This supersedes Section 20's pending-local-validation status. The result validates only the pure-Python injected-provider adapter contract. It does not experimentally verify the installed MetaTrader5 Python package (previously reported as 5.0.6180), compiled-extension behavior, actual MT5 history queries or completeness, broker-specific partial-fill representation, account/terminal isolation, or any reconciliation algorithm.

No MT5 connection, terminal initialization, broker query/action, account activation, order operation, or active V3.1 Runner modification occurred. The adapter remains research-only and is not integrated into a trading worker. A real package/terminal compatibility experiment requires separate explicit authorization.


## 22. Paired order/deal history observation contract authored

After the operator validated the read-only injected-provider adapter (17/17 tests), a narrow offline observation-pair layer was added:

- `scripts/sp2l_history_pair_observation_research.py`
  - pairs one ORDERS result and one DEALS result under the same position lifecycle identifier;
  - rejects wrong result types, swapped query kinds, and mismatched identifiers;
  - reports `BOTH_RESPONSES_VALID` only when both independent results are EMPTY or NON_EMPTY;
  - reports `AT_LEAST_ONE_QUERY_FAILED` if either result is ERROR;
  - preserves both result objects and their raw rows independently; performs no merge, filtering, deduplication, or reconciliation.
- `tests/test_sp2l_history_pair_observation_research.py`
  - 8 synthetic tests authored for empty/empty, non-empty/empty in both directions, independent query failures, mismatched identifiers, and swapped query kinds.
- `docs/research/SP2L_HISTORY_PAIR_OBSERVATION_RESEARCH_2026-11-16.md`
  - defines the paired-observation contract and interpretation limits.

Commits:
- Module: `766ab918f3b376db5fb6b6993b09dacf934f542a`
- Tests: `851cdcb6cc98f04cad8fde2ba903490173d9957d`
- Documentation: `6ff3180c3f31a4384e47ea2601e2696834681efd`

**Validation status:** the 8 new tests are authored but have not yet been run in the operator's local environment. Do not count them as passed until the focused local run succeeds.

**Interpretation boundary:** two empty tuples mean only that both query calls returned recognized empty responses. They do not prove complete history, absence of a position, or permission to bootstrap recovery. The pair layer does not define order/deal linkage, partial-fill behavior, broker semantics, recovery disposition, or execution rules.

No MT5 import, terminal initialization, broker query/action, account activation, order operation, or active V3.1 Runner modification occurred. The new layer is not integrated into a worker or recovery path.


## 23. History-to-recovery gate authored — local validation pending

The paired Order/Deal observation is now connected to the existing offline recovery fixture through a separate fail-closed gate:

- `scripts/sp2l_history_recovery_gate_research.py`
  - requires a typed pair and validates both embedded query results, query kinds, matching position identifiers, and consistency between the pair status and each independent query status;
  - halts if either query failed, the pair is malformed/forged, or the pair's status contradicts its component outcomes;
  - also halts unless `history_completeness_verified=True` is explicitly supplied from an independent evidence source;
  - only after those checks delegates to the existing recovery contract.
- `tests/test_sp2l_history_recovery_gate_research.py`
  - 13 synthetic tests authored, including error propagation, empty-pair insufficiency, explicit independent completeness gate, existing recovery fail-closed conditions, wrong pair type, malformed embedded result, and forged pair status.
- `docs/research/SP2L_HISTORY_RECOVERY_GATE_RESEARCH_2026-11-16.md`
  - specifies gate order and interpretation boundaries.

Commits:
- Initial gate module: `2feb843b3b883dc9036ad28ef79f5f94aea29b16`
- Initial tests: `d6903178e19ecdce911f59339ffd38e456a9a1bd`
- Documentation: `ca2f8469e8850d5412b2898732eddc765004c5db`
- Gate hardening: `6707938d007aab9268f5b691927ed86fa4d139cb`
- Malformed-evidence tests: `b1736ba7b4c8ca33bdbb6d04557680eabc02c4fa`

**Validation status:** 13 new tests are authored but not yet run locally. Do not count them as passed until operator validation.

**Important:** the gate does not calculate or establish history completeness. Two empty tuples are not a completeness proof. The explicit completeness flag must ultimately be backed by a separately specified, source-aligned protocol; until then, no real caller may infer it from query success or emptiness. No production recovery path, MT5 connection, terminal initialization, broker query/action, account activation, order operation, or active V3.1 Runner modification is included.


## 24. History-to-recovery gate — 70/70 synthetic tests locally validated

On 2026-11-16, the operator ran the five focused research test modules together from the dedicated multi-account worktree on branch `research/multi-account-foundation-rfc-20261116`:

- Reported HEAD: `f427f46d38dda92146bc51f3698dc98329dc2c68`
- Test modules:
  - `tests.test_sp2l_read_only_history_adapter_research` — 17 tests
  - `tests.test_sp2l_history_pair_observation_research` — 8 tests
  - `tests.test_sp2l_history_recovery_gate_research` — 13 tests
  - `tests.test_sp2l_multi_account_recovery_contract_research` — 20 tests
  - `tests.test_sp2l_account_isolation_contract_research` — 12 tests
- Result: `TEST_EXIT=0`
- Result summary: `Ran 70 tests in 0.005s — OK`

All 70 tests passed. This supersedes Section 23's pending-local-validation status for the history-to-recovery gate and jointly revalidates the four supporting contract suites in the same run.

**Validation boundary:** this is local pure-Python synthetic validation only. It does not verify the installed MetaTrader5 Python package, actual MT5 history queries, broker history completeness, account/terminal isolation, real recovery, order/deal reconciliation, partial-fill behavior, or worker/runtime behavior. In particular, the independent history-completeness assertion remains an unresolved evidence requirement; successful or empty history responses alone do not establish completeness.

No MT5 connection, terminal initialization, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.


## 25. History-completeness evidence protocol — source-aligned research draft

After the 70/70 synthetic validation, a research-only protocol draft was added:

- `docs/research/SP2L_HISTORY_COMPLETENESS_EVIDENCE_PROTOCOL_RESEARCH_2026-11-16.md`
- Commit: `b1d7e72e0a2f7abf6d51b81a262cba4fde0b97e1`

The draft maps the documented Python history APIs:
- `history_orders_get(date_from, date_to)` and `history_deals_get(date_from, date_to)`;
- corresponding `history_orders_total(date_from, date_to)` and `history_deals_total(date_from, date_to)`;
- MQL5 `HistorySelect(from_date, to_date)`, documented for a specified period of server time.

It proposes preserving the four API observations independently, distinguishing `None` errors from valid empty collections, and treating total-versus-row-count disagreement as an inconsistency. Matching counts are described only as API-level consistency for the requested scope.

**Critical limitation:** the official documentation reviewed does not provide an independent guarantee that the terminal has every record in the broker's backend archive, nor an atomic-snapshot guarantee across the four calls. Therefore API-only evidence cannot currently set `history_completeness_verified=True`. Absolute history completeness remains unresolved; the existing recovery gate remains fail-closed.

The draft does not implement an adapter, query MT5, verify the installed package, establish server-time conversion semantics for the installed environment, reconcile orders/deals, or authorize production recovery. No MT5 connection, broker action, account activation, or active V3.1 Runner modification occurred.


## 26. History-completeness evidence classifier authored — local validation pending

A pure-Python classifier and synthetic test module were added from the research protocol in Section 25:

- `scripts/sp2l_history_completeness_evidence_research.py`
  - commit: `aff5ab1276113bf830b9670a620676f0925052dd`
  - accepts already-captured ORDERS and DEALS total/collection observations; makes no API calls;
  - requires explicit account/session/server/time-scope provenance, observed package/build metadata, and a SHA-256 manifest reference;
  - distinguishes a valid empty tuple from a missing collection (`None`) and captured query errors;
  - detects invalid counts, wrong query kinds, invalid collection shapes, and total-versus-row-count mismatches;
  - returns only descriptive dispositions: INVALID_SCOPE, QUERY_FAILED, COUNT_MISMATCH, or OBSERVED_CONSISTENT_FOR_SCOPE;
  - its completeness helper deliberately always returns false. Matching counts cannot set the independent completeness assertion required by the recovery gate.
- `tests/test_sp2l_history_completeness_evidence_research.py`
  - commit: `ab9cc9ba3eb3bc727aff2738eeba2b0217dd92ee`
  - 18 synthetic tests authored for matching and empty counts, count mismatches, API errors, invalid shapes/counts, scope provenance, opaque error preservation, and the invariant that absolute completeness remains unproven.
- `docs/research/SP2L_HISTORY_COMPLETENESS_EVIDENCE_MODEL_RESEARCH_2026-11-16.md`
  - commit: `67e027015d367c22a2ab439281a1951eae44a388`

**Validation status:** the 18 tests are authored but have not yet been run in the operator's local environment. Do not count them as passing until the operator reports the local result.

**Boundary:** this is a classifier over injected/captured synthetic data, not an MT5 adapter or runtime experiment. It does not prove atomicity, full lifecycle coverage, broker archive completeness, installed-package compatibility, or order/deal reconciliation. It is not integrated into the recovery gate and cannot authorize recovery. No MT5 connection, broker action, account activation, or active V3.1 Runner modification occurred.


## 27. History-completeness evidence classifier — 88/88 local tests validated

The operator ran all six focused research test modules on branch `research/multi-account-foundation-rfc-20261116`:

- Reported HEAD: `7ebb76e7b1807824baee8237747e8218144fec75`
- Test modules: adapter (17), pair observation (8), recovery gate (13), recovery contract (20), account isolation (12), completeness evidence classifier (18).
- Result: `TEST_EXIT=0`; `Ran 88 tests in 0.005s — OK`.

This validates the classifier's synthetic behavior and the supporting contracts together. The classifier only reports API-observation consistency; it cannot prove broker archive completeness and its completeness helper remains deliberately false.

**Boundary:** local pure-Python synthetic tests only. No installed-package compatibility, MT5 runtime, broker archive, actual account history, production recovery, or Runner behavior was tested.


## 28. Repeated history-observation stability model authored — local validation pending

A separate, offline stability comparison layer was added:

- `scripts/sp2l_history_stability_research.py`
  - commit: `fc9762d304f9d923485e37ec3f5ebe3f31db3736`
  - compares two independently captured observations only after each passes the Section 26 API-consistency classifier;
  - requires distinct observation IDs and observed-at values;
  - requires matching account/session/server, interval, time basis/source, package version, and terminal build;
  - compares order/deal counts and externally supplied payload SHA-256 fingerprints;
  - distinguishes invalid observations, insufficient distinct observations, scope mismatch, fingerprint-method mismatch, changed observations, and stable observations.
- `tests/test_sp2l_history_stability_research.py`
  - commit: `53da2310c0304e0b1b20a194f51f6c9b29d0a150`
  - 15 synthetic tests authored.
- `docs/research/SP2L_HISTORY_STABILITY_RESEARCH_2026-11-16.md`
  - commit: `6b1f48ac3d360b6a3cc4de373af2febca149b626`

**Important unresolved input:** the model intentionally does not define raw-row serialization, ordering, field selection, or hashing. The fingerprint algorithm is externally declared and must match across observations. The model does not recompute/verify supplied hashes. This prevents silently inventing data canonicalization or row semantics.

**Interpretation boundary:** STABLE_ACROSS_OBSERVATIONS means only that supplied counts and external fingerprints match across two distinct observations of the same declared scope. It does not prove either snapshot is complete, calls are atomic, or the broker archive has no additional records. The completeness helper deliberately always returns false.

**Validation status:** 15 tests authored; local execution pending. No MT5 connection, terminal initialization, broker action, production recovery integration, account activation, or active V3.1 Runner modification occurred.


## 29. Repeated history-observation stability — 103/103 local tests validated

After the Section 28 stability model was pulled into the dedicated multi-account worktree, the operator ran all seven focused research test modules together:

- Branch: `research/multi-account-foundation-rfc-20261116`
- Local HEAD reported after pull: `8811c5577f0558dd8f81d53cac870780541fd68c`
- Test modules: read-only history adapter (17), paired history observation (8), history recovery gate (13), multi-account recovery contract (20), account isolation contract (12), history-completeness evidence classifier (18), and repeated-observation stability (15).
- Result: `TEST_EXIT=0`
- Result summary: `Ran 103 tests in 0.007s — OK`

All 103 synthetic tests passed in the operator's local project virtual environment. This supersedes Section 28's pending-local-validation status for the 15-test stability module and jointly revalidates the six supporting modules in the same run.

**Validation boundary:** pure-Python synthetic validation only. The stability model compares supplied counts and externally supplied fingerprints; it does not define or verify row serialization, ordering, field selection, or hash generation. Stable repeated observations do not prove history completeness, atomicity, or broker archive completeness. The completeness helper remains deliberately false and the recovery gate remains fail-closed absent independent completeness evidence.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.


## 30. Evidence Manifest record model authored — local validation pending

A new offline-only evidence-manifest record model was added:

- `scripts/sp2l_evidence_manifest_research.py`
  - commit: `72d69d0adb36255d4948388582fce08f787301e9`
  - defines typed manifest and artifact records with opaque account/session references, declared server/time scope, package/build metadata, capture method/tool version, observation IDs, and artifact locators;
  - validates required provenance fields, tuple shapes, unique IDs, nonnegative integer byte lengths, and SHA-256 digest shape;
  - records artifact SHA-256 as a declaration about the exact referenced byte sequence; performs no filesystem access, byte reading, hashing, or digest verification.
- `tests/test_sp2l_evidence_manifest_research.py`
  - commit: `887464cc8db952aa37b873d594957e794d4c1cbf`
  - 16 synthetic tests authored.
- `docs/research/SP2L_EVIDENCE_MANIFEST_RESEARCH_2026-11-16.md`
  - commit: `1dbcc5d05d08b799b3f841d3aea1b1fd94cfa745`
  - documents exact-byte hash meaning, provenance scope, deferred serialization/signature decisions, and limitations.

**Validation status:** the 16 tests are authored but have not yet been run in the operator's local environment. Do not count them as passing until a fresh local run succeeds.

**Deferred by design:** manifest serialization/canonical JSON, self-hash/signature, trusted timestamping, storage immutability, raw MT5 row serialization/order/field selection, and semantic fingerprint generation remain undefined. A valid manifest record does not authenticate its claims, prove that artifact locators exist, or establish history completeness. It cannot set `history_completeness_verified=True`.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.


## 31. Evidence Manifest — 119/119 local synthetic tests validated

The operator pulled the Evidence Manifest model and ran all eight focused research test modules together:

- Branch: `research/multi-account-foundation-rfc-20261116`
- Local HEAD: `1ce8ee4bdf982ab793e183852b6b6cea1824fc26`
- Test modules: read-only history adapter (17), paired history observation (8), history recovery gate (13), multi-account recovery contract (20), account isolation contract (12), history-completeness evidence classifier (18), repeated-observation stability (15), and evidence manifest (16).
- Result: `TEST_EXIT=0`
- Result summary: `Ran 119 tests in 0.008s — OK`

This locally validates the new 16-test Evidence Manifest record model together with all 103 previously validated supporting tests.

**Validation boundary:** synthetic, offline Python tests only. Manifest validation checks declared record shape and provenance fields; it does not read or hash artifacts, authenticate locators or claims, define canonical serialization, or prove history completeness. No production integration is authorized by this result.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.


## 32. Evidence Manifest ↔ History Observation linkage authored — local validation pending

An offline metadata-linkage layer was added:

- `scripts/sp2l_evidence_manifest_linkage_research.py`
  - commit: `dc946065c487cf73c3965a26a132689e97b1101b`
  - validates a manifest record, supplied observation fingerprints and their underlying scoped history evidence;
  - requires supplied observation IDs to be a subset of the manifest's declared observation IDs;
  - checks account identity reference, terminal session reference, server, date interval, time basis/source, package version, and terminal build;
  - returns explicit invalid-manifest, invalid-observation, unlisted-observation, scope-mismatch, or linked-for-declared-scope outcomes.
- `tests/test_sp2l_evidence_manifest_linkage_research.py`
  - commit: `7b5a02353a0c2b8ac8354731c4946641d18a8fce`
  - 14 synthetic tests authored.
- `docs/research/SP2L_EVIDENCE_MANIFEST_LINKAGE_RESEARCH_2026-11-16.md`
  - commit: `f17841c1ff1649fc2c3cc4cecd9d2d8faeb607c5`
  - defines linkage outcomes and non-claims.

**Validation status:** 14 tests authored, not yet run locally. This is metadata linkage only; artifact bytes, locators, hashes, signatures, authenticity, and completeness are not verified. Artifact role names remain operator-declared and no required role schema is inferred. No production or recovery integration is introduced.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.


## 33. Evidence Manifest ↔ History Observation linkage — 133/133 local tests validated

The operator pulled the linkage implementation and ran all nine focused research test modules:

- Branch: `research/multi-account-foundation-rfc-20261116`
- Local HEAD: `981beaf5ea4882a88fcba27a5f3a9bd15ffc3b74`
- Test modules: read-only history adapter (17), paired history observation (8), history recovery gate (13), multi-account recovery contract (20), account isolation contract (12), history-completeness evidence classifier (18), repeated-observation stability (15), evidence manifest (16), and evidence-manifest linkage (14).
- Result: `TEST_EXIT=0`
- Result summary: `Ran 133 tests in 0.008s — OK`

The 14 new linkage tests passed, covering matching scope, listed/unlisted observation IDs, account/session/server/interval/time-basis/package mismatches, invalid history evidence, and duplicate IDs.

**Validation boundary:** offline synthetic tests only. A `LINKED_FOR_DECLARED_SCOPE` result establishes metadata agreement for the supplied observations; it does not verify artifact existence, artifact byte length or digest, content-to-observation correspondence, manifest authenticity, or history completeness. It does not authorize recovery or production integration.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.


## 34. Exact-byte Evidence Artifact Verification authored — local validation pending

An offline filesystem verifier was added:

- `scripts/sp2l_evidence_artifact_verification_research.py`
  - commit: `297d86298acb8e5eb87fcea28178b9af9eb80fb9`
  - accepts an explicit caller-supplied mapping of `artifact_id -> local path`;
  - deliberately does not interpret manifest locator strings or invent URI/root/path-resolution semantics;
  - opens files read-only in binary mode, requires regular files, streams exact bytes in 1 MiB chunks, computes SHA-256, counts bytes, and compares descriptor metadata before/after reading;
  - reports per-artifact missing path, missing file, non-regular file, read error, changed-during-read, byte-length mismatch, digest mismatch, or exact-byte verification;
  - overall success requires every manifest artifact to verify.
- `tests/test_sp2l_evidence_artifact_verification_research.py`
  - commit: `2de44470b6be06dec25aeb08bb7ef261bcb39867`
  - 16 synthetic filesystem tests authored.
- `docs/research/SP2L_EVIDENCE_ARTIFACT_VERIFICATION_RESEARCH_2026-11-16.md`
  - commit: `82e4c842922425394b7d56eabff5c12a0fc33872`
  - documents exact-byte behavior, explicit path resolution, outcomes, and limitations.

**Validation status:** 16 tests authored; local execution pending. Expected focused-suite total is 149 tests (the previously validated 133 plus 16 new artifact-verification tests).

**Interpretation boundary:** successful verification means only that bytes read from the caller-supplied local paths matched the manifest's declared byte lengths and SHA-256 digests. It does not prove file origin, capture time, semantic correspondence to an observation, manifest authenticity, immutability, or history completeness. Before/after file metadata checks are not an atomic snapshot or a defense against every adversarial filesystem race. This layer is not integrated into recovery, MT5, account workers, or the active Runner.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.



## 35. Exact-byte Evidence Artifact Verification — 149/149 local synthetic tests validated

The operator pulled the cross-platform directory-classification correction and reran all ten focused research test modules together:

- Branch: `research/multi-account-foundation-rfc-20261116`
- Local HEAD: `3f513a0e7d1b591b55719b53746878f3e1cd01ee`
- Pull: fast-forward from `9a2f850a` to `3f513a0e`, exit 0.
- Test modules: read-only history adapter (17), paired history observation (8), history recovery gate (13), multi-account recovery contract (20), account isolation contract (12), history-completeness evidence classifier (18), repeated-observation stability (15), evidence manifest (16), evidence-manifest linkage (14), and exact-byte artifact verification (16).
- Result: `TEST_EXIT=0`
- Result summary: `Ran 149 tests in 0.051s — OK`

The initial run exposed a Windows-specific directory classification issue: opening a directory as binary may raise `PermissionError` before descriptor inspection. The verifier was corrected to inspect the path before opening and still verify the opened descriptor is a regular file. The directory test remains intact and now passes.

**Validation boundary:** local pure-Python synthetic tests only. Artifact verification confirms that bytes read from explicitly caller-resolved local paths match manifest-declared byte lengths and SHA-256 digests. It does not prove file origin, capture time, semantic correspondence to history observations, manifest authenticity, immutability, or broker history completeness. The verifier remains research-only and is not integrated into recovery, MT5, account workers, or the active V3.1 Runner.

No MT5 import/initialization, terminal connection, broker query/action, account activation, order operation, production recovery integration, or active V3.1 Runner modification occurred.
