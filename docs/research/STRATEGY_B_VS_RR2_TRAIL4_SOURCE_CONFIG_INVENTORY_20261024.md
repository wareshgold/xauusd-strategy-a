# Strategy B vs RR2/TRAIL4 — source/config inventory (2026-10-24)

**Status: research-only inventory; comparison remains BLOCKED.** This file distinguishes source-confirmed settings from replay assumptions and unresolved semantics. It does not establish a statistical edge, promote Strategy A geometry to canonical, or authorize any live/forward action.

## Safety and scope

- Offline source/documentation audit only. No MT5 initialization, market-data request, order call, runner launch/restart, or state/log/config mutation was performed.
- Strategy B and Strategy A RR2/TRAIL4 remain separate systems. Do not copy settings or execution semantics from one to the other.
- Do not run a paired performance comparison until the blockers in this document and the parent protocol are resolved or explicitly approved as labeled proxy assumptions.
- Preserve all existing datasets and evidence; any later output must use a new unique path.

## Source identities inspected

| Item | Reference | Identity |
|---|---|---|
| Strategy B upstream live bot | [upstream source](https://github.com/AlirezaSadabadi/PythonTraderBot/blob/main/code/SP2L/SP2L_Advanced_Bot_Optimized.py) | Source blob reviewed in the repo audit: `14c936ed1810e8101a4ead74f3536ae6f3a6e4f5` |
| Strategy B source audit/runbook | [source audit](https://github.com/wareshgold/xauusd-strategy-a/blob/research/strategy-b-pythontraderbot-execution-20261022/docs/research/STRATEGY_B_PYTHONTRADERBOT_SOURCE_AUDIT_20261022.md) · [forward runbook](https://github.com/wareshgold/xauusd-strategy-a/blob/research/strategy-b-pythontraderbot-execution-20261022/docs/research/STRATEGY_B_LIVE_FORWARD_RUNBOOK_20261022.md) | Strategy B isolation PR #340 head `cb37a2112911fa42ab3da757d9a2f596ef0a127f` |
| Strategy A RR2/TRAIL4 config | [config file](https://github.com/wareshgold/xauusd-strategy-a/blob/fix/rr2-trail4-pending-lifecycle-safe-20261011/scripts/sp2l_v3_rr2_trail4_config.py) | Branch HEAD `c54fce17c5b6014031775812a517fa0c84eae626`; config blob `5f5c123587bd81028d353560afb8d2763fa33f98` |
| Strategy A RR2/TRAIL4 forward runner | [runner file](https://github.com/wareshgold/xauusd-strategy-a/blob/fix/rr2-trail4-pending-lifecycle-safe-20261011/scripts/run_sp2l_v3_xauusd_forward_test.py) | Runner blob `fdfe34ed15eadf38fa0d24d4a80781357d72328d` |
| Author-replica M1 research replay | [replay script](https://github.com/wareshgold/xauusd-strategy-a/blob/research/sp2l-starnet-engine-integration-20261007/scripts/run-author-replica-mt5-api.py) | Script blob `e10aeb7793259118063b2e4d5e69d40a2c409973` |
| Parent protocol | [paired backtest protocol](./STRATEGY_B_VS_RR2_TRAIL4_BACKTEST_PROTOCOL_20261024.md) | This inventory supplements, not replaces, its gates. |

The author-replica script is a separate research implementation. It must not be treated as either the Strategy B upstream live bot or the RR2/TRAIL4 strategy.

## Settings established by the inspected sources

### Strategy B — upstream live-bot configuration

| Setting | Source-reported value | Interpretation / caveat |
|---|---|---|
| Symbol | `XAUUSD` | Source default is literal; `XAUUSD.ecn` is an adapter choice, not an upstream alias. |
| Timeframe / history | M1 / 500 candles | The upstream notebook uses 10,000 bars; notebook and live bot are separate paths. |
| Polling and candle state | 0.5-second loop; forming M1 candle | Completed-bar-only replay is not equivalent without explicit evidence/approval. |
| Spike body multiplier | 1.5 | Source-reported parameter. |
| P-Gap | 100 broker points | Price distance is points × the configured symbol's broker point; do not hardcode a universal price distance. |
| Maximum SL distance | 1,000 broker points | Same broker-point dependency. |
| TP | 0.9R | Upstream live-bot value; not RR2's TP_R=2. |
| SL anchor | Candle immediately before spike (BUY low / SELL high), with `USE_LOWERLOW_HIGHERHIGH_SL=False` | Source-reported live-bot setting. |
| Filters | EMA60 on; trend filter on; max opposite moves 1; range/ADX, ADX-rising, New York session filters off | Do not tune during comparison. |
| Second entry / size / magic | Off / 0.01 lot / magic 8 (magic 9 inactive) | Notebook's backtest risk sizing is a different convention. |
| Entry/execution | Internal pending-setup state followed by a market deal; current Ask for BUY / Bid for SELL; execution-based TP recalculation can use actual fill | Not the same as a broker-side limit order or the author-replica's theoretical entry price. |
| Backtest cost model | Notebook: realistic-execution model enabled, simulated spread 30 points, simulated slippage 0; OHLC fallback is an estimate | Assumptions, not measured historical costs. Tick replay and live code need parity tests. |

### Strategy A — RR2/TRAIL4 research baseline

| Setting | Value in the inspected frozen config | Evidence / caveat |
|---|---|---|
| Version / symbol / timeframe | `SP2L_V3_XAUUSD_RR2_TRAIL4_20261001` / base `XAUUSD` / M1 | Research variant, not canonical Strategy A. |
| P-Gap / spike multiplier / max SL | 1.0 price units / 1.5 / 10.0 price units | These are config values; source geometry and broker price conversion must remain explicit. |
| TP_R | 2.0 | Must not be replaced with TP_R=1 or Strategy B's 0.9R. |
| Trail | `TRAIL_PIPS=4.0`; `XAU_PIP_SIZE_PRICE=0.1`; therefore configured trail distance = 0.40 price units | This config explicitly uses a 0.1 price-unit pip definition. Do not silently replace it with a 0.01 point convention. |
| Trail activation | Runner checks favorable excursion against `TRAIL_DISTANCE_PRICE` before proposing the new SL | Activation and offset are both tied to the 0.40 distance in this implementation; broker stops/freeze rules may prevent updates. |
| Order mode / SL anchor | `PENDING_LIMIT_RESEARCH` / `SPIKE_CANDLE_EXTREME_RESEARCH` | Explicitly labeled research behavior; do not promote to source-confirmed canonical execution semantics. |
| Pending TTL / session / volume | 30 minutes / `ALL_MARKET_HOURS` / 0.01 | Baseline config values. |
| Trailing timing | Latest completed M1 bar; one decision per tracked position per completed bar in the inspected V3 runner | Intrabar sequencing and fill parity still need synthetic tests. |

The RR2/TRAIL4 config's `find_first_entry` searches later candles for a low/high break relative to the previous candle, derives a theoretical entry and SL, and computes TP from 2R. This is the research config's behavior; it is not evidence that the Strategy A source documents this as canonical entry/fill semantics.

### Author-replica research script — distinct third implementation

The inspected script `run-author-replica-mt5-api.py` defaults to `PGAP_PRICE=1`, `SPIKE_MULTIPLIER=1.5`, `MAX_SL_PRICE=10`, `TP_R=1`, and symbol `XAUUSD.ecn`. It reads M1 bars and labels its historical MT5 timestamp mapping unresolved. It creates theoretical signal entry/SL/TP references and scans subsequent OHLC bars for SL/TP touches, but it does **not** establish that the entry filled, does not store exit candle indexes/timestamps in the current output, and independently scans each signal through the end of the window. Its `totalR = wins - losses` is tied to the script's TP_R=1 accounting and cannot be reused as RR2/TRAIL4 accounting.

Therefore this author-replica JSON is not a valid substitute for either the Strategy B live bot or the RR2/TRAIL4 runner.

## Comparison matrix: proven vs unresolved

| Topic | Established | Still unresolved / blocking |
|---|---|---|
| Strategy parameters | Values listed above are present in inspected source/config/runbook | Exact deployed runtime/config identity for any historical forward event must be tied to its commit and config hash. |
| Source parity | Strategy B live bot and notebook differ (500 vs 10,000 bars, execution path and timing) | No proven byte/behavior parity between notebook, live bot, and any proposed offline replay. |
| Time basis | Author-replica script renders epoch timestamps as UTC and explicitly declares mapping unresolved | Historical MT5/server timestamp mapping; supplied replay has 9,759 raw bars outside requested interval and a retained range that does not span the request. |
| Signal timing | Strategy B polls a forming candle every 0.5 seconds; RR2/TRAIL4 runner trails from completed M1 bars | Exact same-time eligibility, repeat polling, duplicate prevention, and bar-boundary convention in a shared replay. |
| Entry/fill | Strategy B source submits market deals after trigger; RR2/TRAIL4 config is labeled pending-limit research | Price-side, spread/slippage, actual fills/rejections, and any mapping from OHLC touches to fills. A candle touch alone is not proof of a fill. |
| SL/TP and rounding | Strategy B reports TP=0.9R and actual-fill TP recalculation; RR2 config reports TP_R=2.0 | Exact broker rounding/stops constraints and parity of fill-time recalculation. |
| Trailing | RR2 config reports 4 × 0.1 = 0.40 price units and completed-bar updates | Same-bar order of favorable extreme, trail activation/update, SL touch, and real broker modification/fill must be fixed by evidence or labeled assumptions. |
| Ambiguous OHLC | Current author-replica labels same-bar SL+TP as ambiguous | Shared replay needs synthetic tests for both-levels touched, gaps, and exact exit reference; do not choose a favorable path. |
| Concurrency / overlap | Author-replica scans each signal independently | Its output lacks exit times/indexes, so concurrent-position/holding overlap is not determinable. No position cap or pending lifecycle may be invented. |
| Accounting | RR2 config sets TP at 2R; Strategy B source says 0.9R | Trade-level realized outcomes, costs, R denominator, PF, expectancy and drawdown must be independently reproduced from an auditable ledger. Do not infer real RR2 performance from the author-replica's TP_R=1 summary. |
| Costs | Strategy B notebook's spread/slippage assumptions are documented | Historical spread, commission, swap, fees, and slippage for both strategies are not yet evidenced on a common basis. |
| Sample design | One-week and one-month paired protocol is documented | Freeze exact windows/boundaries before inspecting results; if week nests in month, explicitly account for dependence. No parameter search on those windows. |

## Blocking checklist before a paired run

1. Freeze exact source commits, config hashes, symbol specification and a single immutable M1 dataset/hash for both strategies.
2. Reconcile the historical MT5 timestamp mapping, requested interval, out-of-interval rows, duplicates/order and all gaps. Do not shift/fill/discard silently.
3. Declare a replay fidelity class for each strategy: source-observed, tick replay, or explicit OHLC proxy. Strategy B's forming-candle/market-order semantics cannot be claimed reproduced by plain M1 OHLC.
4. Add deterministic synthetic fixtures for signal timing, fills/rejections, actual-fill TP, rounding, simultaneous SL/TP touches, trail activation/update timing, costs, concurrency, and open-at-end.
5. Produce an auditable per-trade ledger with entry evidence, exit candle/event references, position interval, costs, and formula/version. Missing entry/exit evidence stays UNKNOWN / NOT_DETERMINABLE.
6. Validate counts and metrics independently from the ledger; report uncertainty and dependent windows honestly.
7. Only after these gates pass, run the predeclared one-week and one-month paired tests. Then robustness/stability; a fresh untouched holdout only after rules and protocol are frozen.

## Follow-up synthetic source-parity fixtures (2026-10-24)

Added `tests/test_strategy_source_parity_fixtures.py` and wired it into the dedicated read-only research workflow. These tests cover only small deterministic facts read from the sources:

- Strategy B's 100-point P-Gap and 1,000-point maximum SL convert through the configured broker point; same point counts do not imply the same price distance for all symbols.
- Strategy B TP_R=0.9 and RR2/TRAIL4 TP_R=2.0 remain distinct.
- RR2/TRAIL4's inspected configuration calculates 4 × 0.1 = 0.40 price-unit trailing distance and direction-specific stop arithmetic.
- Strategy B's BUY entry candidate checks a current-low break versus the previous low; that condition is not a broker fill confirmation.
- A single OHLC bar touching both SL and TP remains ambiguous without finer event-sequence evidence.

The fixture helpers are intentionally small arithmetic/evidence classifiers, not a shared strategy engine. They do not determine canonical SP2L geometry, simulate broker orders, resolve timestamp mapping, or establish profitability. The tests should run alongside the existing evidence fixtures in the `research-readonly-replay-audits` workflow.

## Current decision

**BLOCKED — do not compute or publish a strategy winner yet.** The parameter differences are now explicitly documented, but time mapping, fill evidence, replay parity, overlap, trailing intrabar ordering, and common historical cost accounting remain unresolved. This document does not define canonical Strategy A rules and does not authorize live orders, forward-test changes, or production decisions.


## Event ledger contract follow-up (2026-10-24)

Added [research-only event ledger contract](./REPLAY_EVENT_LEDGER_CONTRACT_20261024.md) and deterministic fixtures in `tests/test_replay_event_ledger_contract_fixtures.py`. The contract preserves event provenance, source/config/dataset hashes, original timestamps and timezone evidence, source sequence IDs, and distinct Strategy B market-deal versus RR2/TRAIL4 pending-limit profiles.

The fixtures explicitly keep candidates separate from fills, require bounded evidence for a terminal rejection to support `NOT_FILLED`, preserve ambiguous same-time ordering without sequence evidence, and treat `DATA_END` as distinct from `EXIT_FILL`. The dedicated read-only workflow passes for this revision. This is schema/fixture validation only; it does not resolve historical event availability or make the backtest comparison unblocked.


The follow-up [event source-availability audit](./STRATEGY_B_VS_RR2_EVENT_SOURCE_AVAILABILITY_20261024.md) pinned the Strategy B execution adapter (`Meta.py`, blob `5a145fd02c282950b169165eb8b888e904d1fe6a`): it submits market-deal requests and returns MT5 results, but an immutable actual-deal/event artifact is still needed for replay. RR2/TRAIL4 has named lifecycle/deal logging in its runner; the base logger's `ts_utc` is runner observation/write time, while the inspected deal event omits the original broker `deal.time` and source sequence ID. Preserve those as separate missing fields until evidence is available. These are evidence gaps, not permission to infer events.
