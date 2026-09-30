# SP2L Strategy A — Official Research Snapshot
## 2026-09-30

**Repository:** `wareshgold/xauusd-strategy-a`  
**Working branch:** `research/sp2l-legacy-mirror-backtest-20260929`  
**Research status:** NON-CANONICAL FORENSIC / SOURCE-ALIGNMENT RESEARCH  
**Production decision generation:** prohibited by this research stage

---

## 1. Research objective

Determine whether the historical SP2L Strategy A results are reproducible from the exact MT5 Tester population and whether prior discrepancies were caused by data extraction/replay differences.

Canonical rules remain source-first. Backtest performance does not promote unresolved geometry to canonical rules.

Workflow remains:

SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION

---

## 2. Source-aligned facts currently retained

Confirmed/source-aligned items:

- P.GAP is distinct from Common GAP; valid BO is P-Gap.
- F12 trigger: BUY retraces to previous candle Low; SELL retraces to previous candle High. Exact touch/penetration/close semantics remain unresolved.
- F13 2X: secondary entry is 50% of Entry–SL distance.
- F10 stop placement: SL is behind the candle where the Spike started. Exact wick/body/open/close/buffer semantics remain unresolved.

Still unresolved/noncanonical:

- Exact P-Gap geometry/formula.
- Exact AB=CD anchors/tolerance.
- Exact fill semantics.
- Exact SL anchor/buffer semantics.
- Execution/order semantics.
- Any trailing rule.

---

## 3. Exact MT5 Tester forensic fixture

Tester:

- Symbol: XAUUSD.ecn
- Timeframe: M1
- Model: Every tick based on real ticks
- Tester execution window: 2026-01-01 through 2026-09-29
- Exact exported M1 population requested by EA:
  - start Unix UTC: 1758758400
  - end Unix UTC: 1790294400
  - first exported bar: 2025-09-25 01:00
  - last exported bar: 2025-12-31 23:59
  - bars: 94,652

Forensic parameters:

- P-Gap price: 1.0
- Spike multiplier: 1.5
- Max SL: 10.0
- RR: 1.0
- Trail: 10.0 pips = 1.0 XAU price
- Volume: 0.01
- ExportHistoryCsv: true

The EA explicitly reports:

- mode = NON_CANONICAL_FORENSIC
- canonical = false
- same-bar SL+TP = AMBIGUOUS
- intrabar order = NOT_INFERRED_FROM_M1_OHLC
- favorable M1 extreme updates trailing SL for the next candle only

---

## 4. MT5 Tester result

Population/outcome:

- Signals: 1,480
- Decisive: 1,437
- WIN: 1,420
- LOSS: 13
- BREAKEVEN: 4
- AMBIGUOUS: 43
- Open/unresolved: 0
- Decisive win rate: 98.81697982%
- Net R: +721.60007744
- Profit factor: 56.50769826
- Max drawdown: 1R
- Max losing streak: 2
- Trailing activated: 1,113

These numbers are descriptive forensic results only. They are not evidence of a canonical or production-ready edge.

---

## 5. Independent replay validation — PASS

A separate Python replay was run against the **exact M1 CSV exported by the MT5 Strategy Tester**, not against the MT5 Python history API.

History source:

`MT5_TESTER_EXPORTED_M1`

Results:

- bars: 94,652
- signals: 1,480
- mismatch_count: 0
- PASS: true

Replay outcome:

- WIN: 1,420
- LOSS: 13
- BREAKEVEN: 4
- AMBIGUOUS: 43
- Net R: +721.6000774386627

Difference versus Tester net R:

- +0.0000000187R, consistent with floating-point representation.

**Conclusion:** the MT5 Tester result is independently reproducible, row-by-row, on the exact Tester-exported M1 population.

---

## 6. Root cause of the earlier 1,480 vs 1,643 discrepancy

The earlier independent replay using the MT5 Python history API produced:

- Tester signals: 1,480
- Python/API replay signals: 1,643

The API replay also showed anomalous historical retrieval behavior, including incorrect/unrelated returned bars and failed historical calls.

The decisive control experiment was to replace the MT5 Python history API with the exact Tester-exported M1 CSV.

That produced:

- 1,480 vs 1,480 signals
- 0 row mismatches
- PASS = true

Therefore the previous discrepancy is attributable to the **historical data source/retrieval path**, not to an unexplained difference in the replay logic.

---

## 7. Previously established baseline for comparison

On the same one-year forensic population, RR=1 with trailing OFF previously produced:

- Signals: 1,480
- WIN: 1,006
- LOSS: 474
- WR: 67.97297297%
- Net R: +532
- PF: 2.12236287
- Max DD: 7R

RR=2, trailing OFF:

- WR: 44.3243%
- Net R: +488
- PF: 1.5922
- Max DD: 13R

RR=3, trailing OFF:

- WR: 31.6892%
- Net R: +396
- PF: 1.3917
- Max DD: 25R

These are noncanonical descriptive comparisons.

---

## 8. Historical 68% result that motivated this forensic work

A prior exact MT5/Python parity population covering June–August established:

- M1 bars: 63,200
- Signals: 1,060
- Decisive: 1,059
- WIN: 729
- LOSS: 330
- AMBIGUOUS: 1
- Decisive WR: 68.83852691%
- Net R: +399
- PF: 2.20909091

This result was reproducible for that specific population and contract. It does not establish that 68% is universal or live-trading edge.

The current one-year RR=1/no-trailing baseline is also approximately 68% (67.97297%), which makes the next task a **temporal stability and sampling analysis**, not another data-source debugging cycle.

---

## 9. Completed engineering/forensic changes

Relevant repository work completed:

- Added exact MT5 Tester M1 history export to `Sp2lV2Mt5Tester.mq5`.
- Added `--history-csv` support to `forensic_independent_trail10_replay.py`.
- Fixed MQL5 reference compilation issue in the forensic Tester EA.
- Compiled the EA successfully with zero errors/warnings.
- Confirmed the real MT5 Data Folder contains the updated EA and that the Tester loaded the updated EX5.
- Preserved Tester history CSV and trade CSV artifacts under the 2026-09-30 forensic artifact area.

Relevant commits:

- `c8e264c78c34665b2dc4dc05d6da1468ae653bf7` — export exact Tester M1 history.
- `2edae6a94659c0a8d5a894fd01a0cf96de7fa3b0` — replay from Tester history CSV.
- `b7fbcbe239f31256647374539b55d5f137bc06c0` — MQL5 reference compile fix.

---

# 10. NEXT WORK — DO NOT SKIP

## Phase A — Freeze the validated forensic fixture

Use the exact Tester-exported 94,652-bar M1 dataset as the data fixture for subsequent forensic analysis.

Do not use the unreliable MT5 Python historical retrieval path for this historical population.

Do not regenerate the population from another data source unless it is explicitly treated as a new fixture.

## Phase B — Reconcile the 68% result

Run a deterministic comparison of:

1. Same 1,480-signal population, RR=1, Trail OFF.
2. Same 1,480-signal population, RR=1, Trail=1.0 price.
3. The earlier 63,200-bar / 1,060-signal June–August population.

The objective is to determine how the approximately 68% result behaves across separated time windows and under the exact same frozen forensic contract.

## Phase C — Temporal stability

Break the fixed population into predefined, non-overlapping time windows.

Report for each window:

- signals
- decisive
- wins/losses
- ambiguous
- win rate
- net R
- PF
- max drawdown
- max losing streak

No threshold optimization is allowed while performing this stability check.

## Phase D — Sampling/statistical validation

For the fixed contract:

- quantify uncertainty around win rate;
- test whether observed performance is compatible with a materially lower/null benchmark;
- account for sample size and dependence between observations;
- report confidence intervals/effect uncertainty rather than only point estimates;
- distinguish descriptive performance from evidence of a stable edge.

## Phase E — Trail-specific forensic analysis

Only after the baseline population is frozen:

- audit the 459 LOSS→WIN transitions;
- audit the 43 WIN→AMBIGUOUS transitions;
- quantify how much of the +189.60007742R improvement is attributable to trailing;
- test temporal stability of the trailing transformation.

Trail remains noncanonical until source evidence exists.

## Phase F — Fresh holdout

Only after geometry/semantics are frozen and validation is complete:

- select a genuinely untouched future/fresh holdout period;
- run the frozen contract without parameter selection on the holdout;
- preserve the holdout before inspecting outcome metrics.

## Phase G — Production gate

Production is blocked until:

- source semantics are resolved sufficiently for canonical geometry;
- deterministic fixtures exist;
- independent replay passes;
- robustness/stability is demonstrated;
- fresh holdout is untouched and evaluated;
- execution/fill semantics are explicitly resolved;
- statistical evidence supports a reproducible edge.

No AI-generated BUY/SELL decision is permitted as a substitute for this gate.

---

## 11. Current stopping point

**STOP HERE after this snapshot.**

The data/replay parity problem is resolved for the Tester-exported population.

The next research question is now:

> Is the approximately 68% RR=1 baseline reproducible and statistically/stably supported across predefined time windows, rather than being an artifact of a particular extraction path, period, or parameterization?

No new optimization matrix should be started before that question is answered.
