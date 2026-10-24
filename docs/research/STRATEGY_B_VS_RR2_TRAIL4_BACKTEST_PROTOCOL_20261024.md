# Strategy B PythonTraderBot vs RR2/TRAIL4 — comparable backtest protocol (2026-10-24)

## Purpose

Prepare an evidence-controlled comparison of the upstream-derived Strategy B PythonTraderBot and the existing RR2/TRAIL4 baseline on the same XAUUSD.ecn historical windows. This is a research protocol, not a performance result or a production authorization.

The operator requested a one-week and one-month comparison to inform a later decision. No claim that either strategy is better is permitted until the inputs, timing, fills, and exit accounting pass the gates below.

## Safety boundary

- Research only. Do not connect to MT5, call `order_send`, place/modify/cancel orders, or start either forward runner.
- Do not edit Strategy A or Strategy B runtime behavior, forward-test configuration, live state, event logs, or historical source files.
- Do not change either strategy's source settings to make the comparison look better.
- Keep the external PythonTraderBot implementation isolated from Strategy A evidence and state.
- This protocol does not define or promote Strategy A canonical geometry. Unresolved SP2L source semantics remain unresolved.
- Keep generated reports in new, unique output paths; never overwrite source data, manifests, or existing evidence.

## Source-aligned Strategy B configuration to verify

The isolated source copy and runbook in PR #340 document these upstream values. The actual checked-out file must be inspected before a replay is implemented or run:

- M1; 500 candles; source loop polls every 0.5 seconds and uses the forming candle.
- Spike body multiplier 1.5.
- P-Gap = 100 broker points; maximum SL distance = 1000 broker points.
- TP = 0.9R; SL uses the candle immediately before the spike; `USE_LOWERLOW_HIGHERHIGH_SL=False`.
- EMA(60) filter on; trend filter on; maximum opposite moves = 1.
- Range/ADX filter off; ADX-rising filter off; New York session filter off.
- Second entry off; volume 0.01; magic 8 (magic 9 is inactive).
- Source market-order execution and execution-price TP recalculation are retained.
- Symbol adapter is XAUUSD.ecn. The effective price distances depend on the symbol's broker `point`; do not assume a generic gold pip convention.

These are reported source settings, not independently proven replay semantics. Preserve them exactly unless the source owner supplies a correction.

## RR2/TRAIL4 baseline to verify

Use the existing RR2/TRAIL4 V3 config and the documented live trailing behavior as the baseline. Do not import Trail-10/TP_R=1 fallback settings or substitute the fixed-SL/TP experiment.

Previously documented live baseline:
- TP_R = 2.0.
- Trailing distance/activation are both tied to the configured `TRAIL_DISTANCE_PRICE`, currently documented as 0.40 price units.
- RR2/TRAIL4 is a separate strategy/configuration from Strategy B; its settings must not be copied into Strategy B.

Before replay, record the exact config file path, content hash, Git commit, symbol, point/digits, and relevant entry/SL/TP/trailing values. If the selected source/config cannot be identified unambiguously, stop and report the blocker.

## Data contract and time-window gate

Use one immutable, hashed XAUUSD.ecn M1 dataset for both strategies and both windows. The same timestamp rows and the same boundary convention must be used for each paired run.

The supplied replay report currently says:
- expected minute span: 31,681;
- raw bars returned: 31,681;
- filtered bars in interval: 21,922;
- raw bars discarded outside interval: 9,759;
- first retained UTC timestamp: 2026-09-01 01:00;
- last retained UTC timestamp: 2026-09-22 23:58;
- 15 timestamp gaps;
- timestamp basis rendered as UTC, with historical MT5 timestamp mapping unresolved.

These values are a blocking data-integrity warning, not proof that the rows are wrong. Reconcile the requested interval, raw timestamps, broker/server offset, filtering logic, duplicate/ordering checks, and every gap before interpreting performance. Do not silently fill gaps, shift timestamps, or discard additional rows. Emit a machine-readable audit and preserve the original input hash.

The one-week window must be selected before examining its strategy results. The one-month window must be explicitly defined and recorded by inclusive/exclusive UTC boundaries. If the week is nested in the month, label that dependence; do not present the two windows as independent samples.

## Replay fidelity gates

A shared M1 OHLC replay cannot automatically reproduce a strategy that reads a forming candle every 0.5 seconds or submits market orders at Bid/Ask. Before computing performance, document and test:

1. **Signal timing:** which completed/forming candle is read, when a signal becomes eligible, and whether repeated polls can duplicate a signal.
2. **Price side and fill:** the price side used for BUY/SELL, market fill approximation, spread, slippage, and rejected/unavailable quotes. If source semantics cannot be reconstructed from the available data, mark the result as a proxy, not an exact replica.
3. **SL/TP:** exact source calculation, rounding to symbol digits, minimum-distance constraints, and actual-fill TP recalculation for Strategy B.
4. **Intrabar ordering:** when SL and TP are both touched in one bar, mark the outcome ambiguous unless tick/order evidence resolves it. Do not choose the favorable path.
5. **Trailing:** apply only to RR2/TRAIL4, using the baseline's documented activation and offset semantics. Prevent same-bar look-ahead (do not update a stop from a bar's high/low and then use that same bar to claim the updated stop was hit).
6. **Costs:** report gross and net results separately. Net results require supported spread/commission/swap/fee/slippage inputs; do not substitute a current tick-value snapshot for historical costs without labeling it as an approximation.
7. **Position and pending constraints:** record whether concurrent positions, overlapping signals, exposure limits, and broker constraints are source-defined or replay assumptions. Never invent them silently.

If a gate cannot be met, retain a diagnostic/proxy label and state the exact limitation rather than tuning a substitute behavior.

## Required paired outputs

For each strategy and each window, save a unique report bundle containing:
- input dataset hash, manifest reference, exact UTC window, code commit, config hash, and replay version;
- signal count, accepted/rejected/blocked entries, closed trades, open-at-end trades, and ambiguous outcomes;
- wins/losses/breakeven counts with the denominator stated explicitly;
- gross R, net R when supportable, gross/net P&L where historically supportable, profit factor, expectancy per closed trade, and maximum drawdown;
- exit-reason counts, including original SL/TP and trailing exits for RR2/TRAIL4;
- missing-data and replay-fidelity warnings;
- per-trade ledger with stable signal/trade IDs and timestamps.

Do not compare win rate alone. Report the number of observations and uncertainty; include a confidence interval for win rate and a bootstrap or other predeclared uncertainty estimate for expectancy/drawdown where the sample and dependence structure make it defensible. Consecutive trades and overlapping market regimes are not necessarily independent.

## Offline replay-ledger audit

Before interpreting a replay summary, run the read-only ledger diagnostic
`scripts/audit_sp2l_replay_ledger_readonly.py` against the existing JSON using
a new report path or stdout. It checks outcome counts and compares reported
`totalR` / `profit_factor` with a clearly labeled conditional calculation
(`wins × config.tpR − losses`, and `wins × config.tpR ÷ losses`). This arithmetic
is only a diagnostic assumption; it does not prove actual fills, costs, or
profitability.

The current author-replica JSON does not store exit candle indexes/timestamps or
position lifecycle events. Consequently, the tool must report concurrent-position
and holding-overlap status as **not determinable from artifact**. Do not infer
that trades do not overlap merely because each signal has a terminal outcome.
If overlap matters to the comparison, use the proposed
[research-only event ledger contract](./REPLAY_EVENT_LEDGER_CONTRACT_20261024.md)
and its synthetic lifecycle fixtures as the next schema proposal. This contract
does not create missing historical exit references; overlap remains not
determinable until the source artifacts provide sufficient interval boundaries.
Do not rewrite existing evidence.

## Decision sequence

1. Source/config audit.
2. Immutable shared dataset and timestamp audit.
3. Synthetic fixtures for signal timing, fills, SL/TP, ambiguous bars, trailing, accounting, and event lifecycle/order.
4. Freeze the source-aware event ledger schema and adapter profiles; implement replay only after the required source events and timestamp basis are available.
5. Run the one-week and one-month paired comparisons.
6. Inspect trade ledgers and reproduce headline metrics independently from those ledgers.
7. Robustness/stability analysis on predeclared slices; no parameter search on the comparison windows.
8. Only then decide whether a fresh untouched holdout is justified.

A successful unit-test run establishes implementation consistency, not a profitable edge. The two strategies must remain experimental until independent validation supports a decision.

## Current status

**BLOCKED — source/data/replay parity not yet demonstrated.**

The supplied JSON summaries do not contain the full raw rows or complete per-trade ledgers, and the timestamp mapping is explicitly unresolved. Do not treat the reported +36R / PF 1.90 from the replay JSON as validated evidence. The fixed symmetric SL/TP matrix is a separate exit experiment and is not the RR2/TRAIL4 baseline.

## Operator handoff

After pulling this documentation branch, run only offline checks first. Do not start the live Strategy B runner or change the existing RR2/TRAIL4 forward test as part of this comparison. Record the exact local commit, dataset hash, test output, and any blockers before asking for the next research change.


Before implementing a replay adapter, run the [event-ledger schema validator](./EVENT_LEDGER_SCHEMA_VALIDATOR_20261024.md) on immutable snapshots and retain its input SHA-256 and report. A passing schema check is not event-truth validation and does not replace broker deal evidence, timestamp mapping, or source-profile review.


### RR2/TRAIL4 source-field map

The offline field-by-field mapping for the inspected base runner is documented in
[RR2/TRAIL4 event adapter field map](./RR2_TRAIL4_EVENT_ADAPTER_FIELD_MAP_20261024.md).
It distinguishes runner observation time from broker event time and records which
lifecycle fields cannot safely be promoted to actual fills. This narrows adapter
requirements only; it does not remove the immutable snapshot / actual-deal evidence gate.
