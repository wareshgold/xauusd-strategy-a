# V4 Blockers and Unresolved Questions

**Decision:** `NOT_PROVEN`; publication/production is not requested and no production changes were made.

## Blocking evidence gaps

1. **All full-period data manifests fail hash verification.** July, August and September CSV byte hashes differ from the embedded artifact SHA; each acquisition manifest also marks audit fail and historical session-calendar applicability unverified. Existing files were kept unchanged. Re-acquire or explain/reconcile provenance before inferential use.
2. **Runner/helper in-memory version is not provable.** Read-only process enumeration confirmed runner process path, not loaded module bytes. A Python process already running is not introspected or attached to avoid disturbing it.
3. **New MT5 `history_orders_get(ticket)` errors remain root-cause `UNRESOLVED`.** There are 23 unique invalid-parameter errors; the six listed targets are evidenced in state orders and positions, absent from state deals, and each later had position/deal lifecycle events. No safe independent query against the active terminal was performed.
4. **The OHLC backtest is not executable.** Entry is a theoretical trigger-candle extreme; no order book/ticks establish fill, intrabar ordering, broker rejects, pending TTL, latency or slippage. V3 trailing frequently encounters ambiguous same-bar paths, leaving only 15 decisive baseline trades in each month.
5. **Costs not tested.** Spread CSV column units/conversion are not resolved; commission, swap and slippage schedule are unavailable. `net_after_costs` is absent; no net edge can be claimed.
6. **Source canonicalization remains blocked.** P-Gap concept is supported but exact formula/index/threshold is unresolved; AB=CD anchors/tolerance, exact fill model, precise SL price and numeric RR rule are not source-complete. V3/V4 numeric values are research-only.
7. **Historical regime/session labels not validated.** Session calendars originate from current observation; applicability across the historical split is unverified. Do not attribute results to regimes/sessions.

## Requirement groups not fully covered

- Full synthetic order states: partial fills, server cancellation/reject, restart recovery, suppression and delayed close are not covered end-to-end through runner state save/event reconstruction. A narrow helper delayed-close fixture passed.
- Clean raw broker history reconciliation and all missed/omitted MT5 calls: not tested; log gate suppresses repeats and event log cannot reveal raw call volume.
- One week/month ranges were run, but independent audited feed periods, robust regimes, cost/delay/parameter perturbations and full alternative trailing/filter families are `NOT_TESTED`; see [v4_parameter_sensitivity_NOT_TESTED.csv](../backtests/v4_parameter_sensitivity_NOT_TESTED.csv).
- Fresh holdout was run only as a frozen diagnostic; it fails input hash validation and cannot serve as valid confirmatory holdout. Any future tuning after seeing it requires a new untouched period.
- Trade-level pairing covers research signal keys, not broker order/position/deal fills. The V3 proxy baseline and V4 hypothesis are not directly matched to live events.
- Dependency lockfile hash and exact MT5 terminal build were not captured in baseline manifest; these are additional reproducibility gaps.

## Unresolved hypotheses (not causes)

For `history_orders_get(ticket)` returning `None`/(-2, Invalid params), possible explanations include API call-form semantics or ticket-context expectation; unavailable/not-yet-visible history record; wrong or stale ticket in a particular state; local state/order-position ID conflation; terminal IPC/server behavior; version/runtime discrepancy. Current artifacts do not discriminate among them. Keep conclusion `UNRESOLVED`.

## Human review needed next

1. In the independent worktree, inspect the frozen design, matrix and data-provenance gate. Do not edit the source runner as part of that review.
2. Reconcile why manifest-embedded data SHAs differ from the exact CSV files in this worktree before any statistical interpretation.
3. If safe and independently authorized, design a read-only MT5 API reproduction only after the active runner's impact is understood; do not add it to the active terminal or issue trade calls.
4. Obtain authoritative broker spread/commission/swap/slippage conventions and tick-level fills or approve a conservative cost model before re-running paired comparisons.
5. Resolve remaining source geometry with primary/source owner evidence; do not promote numerical research values.
6. Reserve genuinely fresh untouched validation after all data/model decisions are frozen.
