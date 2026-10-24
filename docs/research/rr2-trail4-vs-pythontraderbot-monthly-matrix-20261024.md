# RR2/TRAIL4 vs Strategy B — Monthly comparison matrix

**Created:** 2026-10-24  
**Status:** Source-aligned candidate replay harness committed; local replay still needs to be run against the user's CSV. Realized performance is intentionally unresolved.  
**Purpose:** Research-only historical comparison. This is not a forward-test change and does not authorize production signals.

## Frozen comparison window

- Target window: 2026-09-24 through 2026-10-23 UTC (the last complete 30-day dataset previously audited).
- Shared instrument: XAUUSD.ecn, M1.
- Previously identified local dataset: `D:\\Mirzaei\\Private\\1\\sp2l-mt5-market-data\\20261024T075827Z\\xauusd_ecn_m1_30d.csv`
- Previously reported dataset SHA-256: `b0782e716e7ccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285`
- Previously reported structural audit: 29,919 rows; zero duplicate timestamps; 21 gap segments; 12,802 missing minute slots; trailing unobserved slots 480. Structural PASS is not a claim of complete market coverage or strategy profitability.

## Source-aligned parameter matrix

| Parameter | Strategy A: SP2L V3 RR2/TRAIL4 | Strategy B: PythonTraderBot / Gold-Spike |
|---|---|---|
| Source | `scripts/sp2l_v3_rr2_trail4_config.py` on `research/sp2l-rr2-trail4-daily-replay-20261008` | `scripts/strategy_b_pythontraderbot_live/SP2L_Advanced_Bot_Optimized.py` at Strategy B commit `0037c540` on `research/strategy-b-pythontraderbot-forward-20261022` |
| Version/profile | `SP2L_V3_XAUUSD_RR2_TRAIL4_20261001` | `src/live_trader.py` v4.1 |
| Spike multiplier | 1.5 | 1.5 |
| P-Gap | 1.00 price units | 100 broker points; 1.00 price units if point=0.01 |
| Max SL distance | 10.00 price units | 1,000 broker points; 10.00 price units if point=0.01 |
| Initial target | 2R | 1R |
| Initial SL anchor | Source inconsistency: config label says `SPIKE_CANDLE_EXTREME_RESEARCH`, but `find_first_entry()` indexes `candles[start_index-2]` (pre-spike candle extreme). Must remain flagged unresolved until the intended anchor is source-confirmed | Previous-to-spike candle extreme as coded in Strategy B |
| Entry/execution | Pending limit research mode | Entry condition is based on current bar low/high and then the bot's own execution path |
| Trailing | 4 configured pips × configured XAU pip size 0.1 = 0.40 price units; completed-M1-bar update in runner | No trailing stop parameter in the inspected source settings |
| Second entry | Candidate includes a secondary-entry level; must verify whether this profile actually places it in the historical replay | Disabled |
| EMA filter | Not assumed; use the A detector and runner source, not B's filters | Enabled, EMA 60 |
| Trend filter | Not assumed; use A's own code | Enabled, max opposite moves = 1 |
| ADX/range filter | Not assumed | Range filter disabled (ADX period 14 / minimum 20 are configured but not active while range filter is false) |
| Session filter | All market hours | Disabled |
| Position size | 0.01 lot | 0.01 lot |

## Performance results

No values are populated until both source implementations have actually been replayed on the same data. Do not fill this table from live-forward results or from unrelated historical parameter sweeps.

| Metric | Strategy A: RR2/TRAIL4 | Strategy B: PythonTraderBot |
|---|---:|---:|
| Data rows actually consumed | NOT RUN | NOT RUN |
| Signals / setups | NOT RUN | NOT RUN |
| Filled entries | NOT RUN | NOT RUN |
| Closed trades | NOT RUN | NOT RUN |
| Wins / losses / unresolved | NOT RUN | NOT RUN |
| Net P&L after costs | NOT RUN | NOT RUN |
| Total R | NOT RUN | NOT RUN |
| Profit factor | NOT RUN | NOT RUN |
| Maximum drawdown | NOT RUN | NOT RUN |
| Pending/unfilled/cancelled orders | NOT RUN | NOT RUN |
| Open positions at window end | NOT RUN | NOT RUN |

## Execution and integrity requirements

1. Both strategies must read the same CSV and identical UTC window; record input SHA-256 in each report.
2. Preserve each strategy's own signal logic, stop/target rules, filters, trailing, and entry path. Do not homogenize rules to make the comparison easier.
3. Do not silently assume intrabar event order when a candle touches both stop and target. Use tick data if available; otherwise mark the case ambiguous or use an explicitly labelled conservative policy.
4. Apply spread/commission/swap only when the data or source supports those values; list any unavailable costs.
5. Report open and unresolved trades separately. No lookahead, no optimizing on this month, no production decisions.
6. The CSV above is on the user's Windows filesystem, not in this GitHub repository. GitHub Actions cannot read that local path. A workflow can only replay it after the data is safely made available to the runner (e.g. as a versioned research input or uploaded workflow artifact). Do not substitute the empty placeholder `artifacts/mt5_xauusd_m1_10000.json` or claim that the backtest ran when it did not.

## Next execution step

Use a research-only replay harness that imports the frozen A configuration and the exact Strategy B source, validates the input manifest/hash, writes machine-readable per-trade ledgers and this metrics table, and attaches the outputs to the run. If the exact fill semantics cannot be established from source, keep the affected metric explicitly unresolved rather than inventing a rule.


## Replay harness

A research-only script is committed at `scripts/research/compare_rr2_trail4_vs_strategy_b_monthly.py`. It reads the local CSV, validates the timestamp/OHLC columns and duplicate timestamps, filters the UTC window, records the input SHA-256, and writes separate candidate ledgers plus a summary. Candidate counts are not realized trades. It deliberately does not invent fills, exits, P&L, PF, or drawdown from M1 OHLC.

From the repository root in PowerShell, run this single command (read-only to the data and forward-test runtime; writes only to a new research output directory):

```powershell
$Repo = (Get-Location).Path
$Csv = 'D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv'
$Py = if (Test-Path (Join-Path $Repo '.venv\Scripts\python.exe')) { Join-Path $Repo '.venv\Scripts\python.exe' } else { (Get-Command python).Source }
& $Py (Join-Path $Repo 'scripts\research\compare_rr2_trail4_vs_strategy_b_monthly.py') --csv $Csv --out (Join-Path $Repo 'artifacts\monthly_strategy_comparison_20261024')
if ($LASTEXITCODE -ne 0) { throw "Research replay failed with exit code $LASTEXITCODE" }
```

Outputs: `comparison.md`, `summary.json`, `strategy_a_candidates.csv`, and `strategy_b_candidates.csv`.

**Important:** The B candidate replay is an independent candidate scan, not a single-position account simulation. The script does not read or modify any forward-test process, orders, state, or logs. P&L metrics remain unavailable until fill/exit semantics are resolved using source-confirmed behavior or tick-level evidence.

## Safe isolated execution (preferred)

To keep existing worktrees, local modifications, and both forward tests untouched, use this PowerShell block. It clones the research branch into a new sibling folder, verifies the exact audited CSV SHA-256, and writes results only inside that new clone:

```powershell
$ErrorActionPreference = 'Stop'
$Branch = 'research/rr2-trail4-vs-pythontraderbot-monthly-matrix-20261024'
$Repo = 'D:\Mirzaei\Private\1\xauusd-strategy-a-monthly-matrix-20261024'
$Csv = 'D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv'
if (Test-Path $Repo) { throw "Safety stop: target already exists; nothing was changed: $Repo" }
if (-not (Test-Path $Csv -PathType Leaf)) { throw "CSV not found: $Csv" }
git clone --branch $Branch --single-branch https://github.com/wareshgold/xauusd-strategy-a.git $Repo
if ($LASTEXITCODE -ne 0) { throw 'git clone failed' }
$Py = (Get-Command python -ErrorAction Stop).Source
& $Py (Join-Path $Repo 'scripts\research\compare_rr2_trail4_vs_strategy_b_monthly.py') --csv $Csv --out (Join-Path $Repo 'artifacts\monthly_strategy_comparison_20261024')
if ($LASTEXITCODE -ne 0) { throw "Research replay failed with exit code $LASTEXITCODE" }
Get-Content (Join-Path $Repo 'artifacts\monthly_strategy_comparison_20261024\comparison.md')
```

Expected CSV SHA-256 is enforced by the script: b0782e716e7ccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285. A mismatch stops the run rather than silently testing a different file.

Note: the harness transcribes the A configuration and B setup/filter logic for a research-only independent candidate scan. It does not import or execute the live bot module, which has MT5 initialization and execution side effects.