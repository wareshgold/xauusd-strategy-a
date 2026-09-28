# SP2L Strategy A — Current State Snapshot
Date: 2026-09-28
Purpose: preserve the exact research/forward-test state so future work resumes from the same point without branch, geometry, or methodology confusion.

## 1. Canonical repository / branch
- Repository: `wareshgold/xauusd-strategy-a`
- Active research branch: `research/sp2l-clean-forward-xau-eurusd-usdjpy-20260928`
- Branch HEAD at snapshot: `1dc8887e10cb62439d4ea68ea7f50c616313dd01`
- HEAD message: `document legacy author replica backtest and forward boundary`
- This branch is the continuation point. Do not silently switch branches.

## 2. Research objective
We are not declaring Strategy A canonical yet.
The objective is to establish a reproducible statistical edge while preserving source meaning.

Required workflow:
SOURCE RESOLUTION -> SYNTHETIC FIXTURES -> FROZEN GEOMETRY -> DEV -> UNTOUCHED VALIDATION -> ROBUSTNESS/STABILITY -> FRESH HOLDOUT -> PRODUCTION

Rules:
- Source meaning outranks backtest performance.
- Only source-confirmed rules can become canonical.
- Unresolved geometry stays explicitly unresolved.
- No invented P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules.
- AI must not autonomously define canonical geometry or generate production BUY/SELL decisions.

## 3. Forward test currently running
Runner:
`scripts/run_sp2l_author_replica_legacy_forward_test_20260928.py`

Mode:
`RESEARCH_AUTHOR_REPLICA_MULTI_SYMBOL_FORWARD_TEST`

Canonical:
`false`

Instrument:
- XAUUSD -> broker symbol XAUUSD.ecn
- M1
- Demo account
- Server: OtetGroup-MT5
- trade_mode: demo (0)
- XAUUSD.ecn trade_mode: 4 (FULL)

Exact research configuration:
- P-Gap price parameter: 1.0 price unit
- Spike multiplier: 1.5
- Max SL distance: 10.0 price units
- TP: 1R
- Volume: 0.01
- Order mode: PENDING_LIMIT_RESEARCH
- Pending TTL: 30 minutes
- SL anchor: SPIKE_CANDLE_EXTREME_RESEARCH
- Session window: London open through New York close

IMPORTANT:
- maxSLDistance=10.0 is 10.00 XAU price units, not 10 pips. With XAU pip_size=0.01, this is 1000 pips.
- This is legacy author-replica research execution, not canonical Strategy A.
- Do not change this forward configuration because of current backtest/forward differences.

Forward startup:
- Started successfully on 2026-09-28 around 10:36:57 UTC.
- Telegram startup delivery encountered an SSL handshake timeout:
  `<urlopen error _ssl.c:993: The handshake operation timed out>`
- A separate Telegram connectivity test was then started in PowerShell 2 and was still hanging at the time of this snapshot.
- Forward process itself must remain untouched while Telegram connectivity is diagnosed separately.

## 4. Historical legacy author-replica backtest
Runner:
`scripts/run-author-replica-mt5-api.py`

Data:
- XAUUSD.ecn
- M1
- MT5 `copy_rates_from`
- 2026-08-26 through 2026-09-25

Fresh result:
- raw bars: 44,640
- filtered bars: 31,574
- gap_count: 22
- signals: 168
- wins: 106
- losses: 58
- ambiguous: 4
- open/unresolved: 0
- decisive win rate: 64.634146%
- total R: +48R
- profit factor: 1.827586

Historical outcome semantics:
- Signal geometry uses the preserved legacy author-replica detector.
- Entry is trigger candle extreme.
- Historical outcome evaluation begins after the signal and resolves by subsequent candle TP/SL ordering; same-candle TP+SL is ambiguous.
- These historical semantics are NOT assumed to be identical to forward pending-order fill semantics.

## 5. Why we are running the forward test
The 64.63% historical legacy result is not being promoted to canonical truth.
The forward test exists to collect real MT5 execution/fill/lifecycle evidence using the same preserved legacy signal geometry/configuration while keeping execution semantics explicit.

The key research question is:
Can we reproduce and explain the observed historical author-replica behavior under actual forward MT5 conditions, and if not, exactly where the discrepancy comes from?

We must distinguish:
1. signal detection parity,
2. candle/data parity,
3. entry/fill semantics,
4. SL/TP semantics,
5. pending-order lifecycle,
6. broker execution constraints,
7. outcome accounting.

## 6. Source-aligned geometry boundary
Frozen Geometry remains BLOCKED.

Known source-confirmed items include:
- F12: BUY retraces to previous candle Low; SELL to previous candle High.
- F13: 2X secondary entry is 50% of Entry-SL distance.
- F10: SL is behind the candle where the Spike started.

Still unresolved and therefore NOT canonical:
- exact P-Gap formula / numeric threshold
- F12 touch vs penetration vs close semantics
- F10 exact wick/body/open/close/buffer semantics
- pending-order fill semantics and bar ordering
- AB=CD anchors/tolerance
- spike magnitude definition and numeric threshold
- exact old candle-role relationships
- C02 50-80 pip convention and RR 1:2 instrument convention

The old P-Gap=1, spike multiplier=1.5, maxSL=10, old SL=A-low/high, and old outcome semantics are diagnostic/replica parameters only.

## 7. Forensic evidence already established
A historical MT5 API parity forensic showed exact equality between `copy_rates_range` and `copy_rates_from` in the tested windows, so those tested API windows did not explain the forward discrepancy.

Signal forensic on XAUUSD.ecn/M1:
- old signals: 168
- current shared-detector signals: 213
- common: 167
- old-only: 1
- current-only: 46
- SL differences on common signals: 167
- outcome differences: 71
- diagnostic integrity mismatch: 0

Counterfactual diagnostics showed that changing SL and/or outcome semantics materially changes results. These are diagnostics only and do not define canonical rules.

## 8. Immediate next steps
1. Leave the current legacy forward runner running unchanged so it can collect forward evidence.
2. Diagnose Telegram connectivity separately in PowerShell 2; do not restart or modify the forward runner just for Telegram.
3. Preserve all forward events/state and later analyze actual fills, cancellations, lifecycle, and outcomes.
4. Compare forward evidence against the exact 168-signal legacy historical replica without changing the replica to fit forward results.
5. Resolve source geometry independently. Backtest performance cannot decide unresolved source meaning.
6. Only after source rules are frozen: synthetic fixtures -> deterministic validation -> untouched validation -> robustness/stability -> fresh holdout.
7. Production execution remains out of scope until the source-aligned system and statistical evidence pass the required gates.

## 9. Operational principle
Do not optimize the strategy to make the forward test look like the backtest.
Do not modify the forward test because of a losing/winning outcome.
First preserve evidence; then explain the discrepancy; then resolve source meaning; then validate.

Snapshot status: FORWARD RUNNING / TELEGRAM DIAGNOSTIC IN PROGRESS / FROZEN GEOMETRY BLOCKED / NON-CANONICAL RESEARCH ONLY
