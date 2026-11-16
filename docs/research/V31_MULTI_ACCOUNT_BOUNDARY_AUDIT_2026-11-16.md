# V3.1 → Multi-Account Boundary Audit (Research Only)

**Date:** 2026-11-16  
**Status:** read-only source audit; non-canonical; no MT5 connection; no live changes.  
**Branch:** `research/multi-account-foundation-rfc-20261116`

## Scope and method

Reviewed the V3.1 XAUUSD wrapper, its imported author-replica runner, trailing state/rules, startup inventory recovery, runner lock, and the earlier Fati offline adapter. This is a source-level boundary map, not a runtime or broker-topology verification.

The active V3.1 Runner and its worktree were not modified, stopped, restarted, or connected to by this audit.

## 1. Current V3.1 runtime boundaries

### MT5 connection and account identity

- `run_sp2l_author_replica_multi_symbol_forward_test.py` owns the process-level `mt5.initialize()` / `mt5.shutdown()` lifecycle.
- Startup reads `mt5.account_info()` and currently enforces DEMO trade mode. It does **not** compare the observed broker, server, and login against an independently configured expected account identity.
- The V3.1 wrapper imports the same `MetaTrader5` module and the base runner in one Python process. Trailing, lifecycle, recovery, and entry code therefore share that process's MT5 connection.
- The exact safe topology for two accounts/terminals is not established by this source review. Do not assume multiple account sessions can share one Python MT5 IPC binding or one terminal process.

### Order ownership and execution

- Entry execution is delegated through `execute_candidate()` to `live_mt5_gateway`; the base runner sets the configured per-symbol magic before execution.
- The V3.1 wrapper fixes XAUUSD and magic base `26092300`, giving its XAU slot magic `26092301`.
- V3.1 lifecycle and trailing paths filter broker objects by symbol and magic. Startup recovery also classifies active orders and positions by exact symbol + magic.
- Symbol + magic is a strategy/worker ownership filter, **not** an account identity proof. Different accounts may legitimately reuse a magic number; account identity must be verified separately before any future account worker may act.

### State, events, and recovery

- The base runner derives `ARTIFACTS` and `RUNTIME` from the worktree root and defines one events JSONL and one state JSON path. V3.1 overrides these to its own V3.1-specific filenames, but not to an account namespace.
- `load_state()` catches any exception and returns an empty state. This includes malformed or unreadable state. That behavior is not acceptable as-is for a multi-account worker: missing, corrupt, or schema-incompatible account state must be distinguished and fail closed where ownership/recovery could be ambiguous.
- `reconcile_state_from_events()` rebuilds tracking from the event stream; malformed JSON lines are skipped and an OS read error returns without a hard failure. This is a legacy recovery behavior to characterize with fixtures, not a safe account-isolation contract.
- V3.1 startup recovery distinguishes MT5 query failure (`None`) from a valid empty inventory and aborts if either active-order or active-position inventory is unavailable. It then records only matching symbol + magic objects and persists the recovered state before startup continues.
- Startup recovery does not itself establish expected account broker/server/login identity.

### Process lock

- The runner lock defaults to a shared temp-path lock, intentionally coordinating runner worktrees on the same host. It prevents concurrent runner processes from duplicating orders.
- A future multi-account design must not simply remove or bypass this protection. It needs an explicitly reviewed lock hierarchy and account-scoped ownership while preserving protection against duplicate workers for the same account.

## 2. Fati adapter audit against latest approved constraints

The previously audited `fati_adapter_orchestration_research.py` is offline-only: it has no MT5, network, Telegram, or primary Runner imports. It builds an inert initial order intent and evaluates supplied observations; it is not an account worker, broker adapter, TP manager, or recovery implementation.

Important policy conflict:
- That adapter imports the earlier RR1 → BE+5 policy and can propose a stop modification.
- The latest Fati design constraint is fixed initial SL, no trailing SL, and Fati-owned TP management.
- Therefore the BE+5 adapter/policy must **not** be reused or wired into a Fati worker until the operator explicitly resolves the conflict. For now, BE remains unresolved and the initial SL stays fixed in the design.
- Fati's Pending Order / Order Filled-only private notification routing is a requirement, not an implemented or validated delivery path in this adapter.

## 3. Required design changes before any worker implementation

1. Add an account-bound MT5 adapter contract that verifies broker, server, and opaque login reference before inventory queries or any possible action. Never log raw credentials; keep account login references protected and opaque.
2. Prove the terminal/process topology experimentally in a separate, explicitly authorized offline/demo test environment. Do not experiment using the active V3.1 terminal or Runner.
3. Define account-scoped state, events, recovery journal, lock, evidence manifest, and magic allocation. Reusing magic values across accounts must remain safe because account identity and state namespace are independently enforced.
4. Replace silent state reset with explicit missing / valid / corrupt / incompatible classifications and fail-closed recovery behavior in the **new research worker only**.
5. Build synthetic fixtures for: cross-account inventory isolation; duplicate signal delivery; duplicate order intent; state corruption and schema drift; missing/stale broker inventory; partial event journal; restart after submit-before-persist; and ambiguous order/position linkage.
6. Keep account policy adapters pure and separately tested. Fati's TP ownership and notification rules must be specified without importing the unresolved BE+5 behavior.
7. Only after these contracts pass should a research-only worker skeleton be considered. No broker action or account activation is implied.

## 4. Explicit non-goals

- No change to the active V3.1 Runner, its state/events, trailing logic, or execution behavior.
- No MT5 initialize/connect/query, terminal launch, order placement/cancellation/modification, or Telegram delivery.
- No Fati account connection or activation.
- No canonical SP2L geometry or production BUY/SELL decisions.
- No assumption that source-level review proves runtime isolation.

## 5. Validation status

- Account identity namespace contract: 12 synthetic unit tests passed locally on 2026-11-16 (`TEST_EXIT=0`).
- This result validates only the pure-Python identity/namespace helper. It does not validate MT5 account identity extraction, terminal isolation, order ownership, recovery, or worker behavior.
