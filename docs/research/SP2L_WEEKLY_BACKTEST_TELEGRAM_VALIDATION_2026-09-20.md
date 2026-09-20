# SP2L Weekly Backtest → Telegram Report Validation — 2026-09-20

Branch: `research/sp2l-live-mt5-telegram-2026-09-19`

Validation/reporting run only: the previous completed trading week
(2026-09-14 → 2026-09-18) backtest results are fed through the deterministic
Telegram reporting system. **No SP2L strategy rule, P-Gap definition, AB=CD
logic, or Leg1/Leg2 assumption was modified. No parameter was optimized. No
live trading was enabled (`LIVE_TRADING_ENABLE=false`).**

## Phase 1 — Canonical backtest path (audit result)

- **Author replica runner (canonical):**
  `scripts/run-author-replica-mt5-api.py` and the `run-author-replica-mt5-*`
  family (direct MT5 M1 replay, research-only, no orders). Requires a
  connected local MT5 terminal.
- **Non-overlap / stability runners:** `run-author-replica-mt5-nonoverlap-stability.py`,
  `run-author-replica-mt5-4week-stability-matrix.py`,
  `run-author-replica-mt5-fresh-holdout.py` (fresh holdout stays locked).
- **Validation harnesses:** `sp2l-fixture-runner.test.ts` /
  `sp2l-determinism-invariants.test.ts` (TS core), `metric-accounting-audit.test.ts`.
- **Journal writers:** `scripts/live_journal.py` (signals/trades/snapshots/report_log JSONL).
- **Offline dataset:** `data/historical/xauusd-1min.json` covers
  2026-08-20 → 2026-08-27 only — it does **not** cover the previous week, so
  the offline `.mjs` path cannot run this window.
- **Canonical previous-week data source (used here):**
  `artifacts/SP2L_author_replica_2026-09-14_2026-09-18.json` — the committed
  research-only author-replica MT5 M1 replay output for exactly this week
  (`research_only: true`, 10000 bars, 2026-09-09T18:12Z → 2026-09-18T23:57Z,
  config pGapPrice=1.0, spikeMultiplier=1.5, maxSlPrice=10.0, tpR=1.0).
  The emitting script variant for this exact artifact schema is no longer in
  the tree; re-implementing a runner was rejected to avoid redefining any
  strategy semantic, so the committed artifact is consumed as-is.

**Documented run profile:** input = MT5 terminal M1 bars for XAUUSD.ecn;
timeframe = M1; date range = trading week 2026-09-14 → 2026-09-18 (UTC);
strategy implementation = author-replica candidate (research-only, not
canonical Strategy A geometry); known limitations = author-replica is not
the canonical engine, outcome model is bar-based (TP/SL same bar ⇒
AMBIGUOUS), no spread/slippage/commission modeling, no broker holiday
calendar, pips require explicit pip size.

## Phase 2 — Trade journal

`scripts/backtest_weekly_journal.py` converts the artifact into
report-engine journal rows (kept **separate from the live journal** in
`runtime/journal_backtest/`, gitignored):

- signal rows: `signal_id` (`BT-20260914-NNN`), status APPROVED, direction,
  entry/SL/TP, timestamp, source `AUTHOR_REPLICA_MT5_M1_REPLAY_BACKTEST`.
- trade rows: status CLOSED (or OPEN if unresolved), result WIN/LOSS/None,
  `r_multiple`, exit price/time, `pips` (explicit pip size 0.1),
  `holding_minutes`, backtest reason.
- AMBIGUOUS (`SL_AND_TP_SAME_BAR`, exit price unknown) → CLOSED with
  result None and R None; nothing is invented to resolve it.

Full required-field trade journal artifact:
`artifacts/SP2L_weekly_backtest_trade_journal_2026-09-14_2026-09-18.json`
(fields: signal timestamp, direction, entry, stop loss, take profit, exit
time, exit price, result, pips, R multiple, holding minutes, reason).

## Phase 3 — Validation

`artifacts/SP2L_weekly_backtest_validation_2026-09-14_2026-09-18.json`:

- 38 signals / 38 trades; **0 duplicate signal IDs; 0 duplicate
  (time,direction,entry) keys; 0 open/unresolved rows; 0 unparsable
  timestamps**; 1 CLOSED row without determinate outcome (the AMBIGUOUS
  same-bar case); 1 CLOSED row without exit price (same row).
- Engine classification over converted rows reproduces the source summary
  exactly (27/10/1, net R 17, PF 2.7) → `consistency_ok: true`.
- Daily UTC breakdown (10/13/3/5/7) matches the source `date_utc`
  distribution exactly.

## Phase 4 — Weekly report (via `scripts/run_sp2l_report.py`)

Run with `REPORT_PIP_SIZE=0.1`, `REPORT_SESSION_TIMEZONE=UTC` (dataset
timestamps are canonical UTC; explicit config, not a new assumption) and
`--journal-dir runtime/journal_backtest`. Artifact:
`artifacts/SP2L_weekly_backtest_report_2026-09-20.json` (+ CSV + XLSX).

```
SP2L Weekly Report — RESEARCH
Trading Period: 2026-09-14T00:00:00+00:00 → 2026-09-19T00:00:00+00:00 (UTC)

Signals:
- Total signals: 38
- WIN count: 27
- LOSS count: 10
- AMBIGUOUS count: 1

Performance:
- Net pips: 643.40 (basis: EXPLICIT_PIP_SIZE)
- Net R: 17.0000
- Profit factor: 2.7000
- Win rate: 72.97%
- Max drawdown: 2.0000 R

Execution:
- Open trades: 0
- Closed trades: 38
- Broker reconciliation status: PARTIAL

Daily breakdown (UTC):
- 2026-09-14: signals=10 win=9 loss=0 ambiguous=1 net_r=9.0000
- 2026-09-15: signals=13 win=9 loss=4 ambiguous=0 net_r=5.0000
- 2026-09-16: signals=3 win=2 loss=1 ambiguous=0 net_r=1.0000
- 2026-09-17: signals=5 win=4 loss=1 ambiguous=0 net_r=3.0000
- 2026-09-18: signals=7 win=3 loss=4 ambiguous=0 net_r=-1.0000

System:
- Geometry status: UNRESOLVED_FROZEN_GEOMETRY_GATE
- Live trading status: DISABLED (LIVE_TRADING_ENABLE=false)
```

`Broker reconciliation status: PARTIAL` is correct here: the journal is a
backtest view, so rows carry exit prices but no broker deal/net fields.

## Phase 5 — Telegram destination status and delivery test

Per the Telegram destination rules (no new bot, no guessed chat IDs; only
existing `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`):

```
bot_configuration_detected: no
chat_destination_configured: no
delivery_mode: MOCK
```

Neither variable is set in the environment or in
`runtime/live-trader.env.example` (placeholders only). The pre-delivery
status is now printed by the CLI and recorded per delivery
(`delivery_mode` field in `runtime/journal/report_log.jsonl`):

```json
{"delivery_mode": "MOCK", "success": false, "telegram_status": "NOT_CONFIGURED", ...}
```

Formatting, template sections and delivery logging were verified offline
with the mock transport (`tests/test_live_report_telegram.py`,
`tests/test_backtest_weekly_journal.py`). **No successful Telegram delivery
is claimed or faked.** A REAL-mode send requires the operator to configure
the existing variables only — no code change, no new bot.

## Phase 6 — Artifacts

- `artifacts/SP2L_weekly_backtest_report_2026-09-20.json` (report, schema `sp2l.live_report.v1`)
- `artifacts/SP2L_weekly_backtest_report_2026-09-20.xlsx` (openpyxl workbook: summary + signals + trades)
- `artifacts/SP2L_weekly_backtest_trade_journal_2026-09-14_2026-09-18.json`
- `artifacts/SP2L_weekly_backtest_validation_2026-09-14_2026-09-18.json`
- `runtime/exports/reports/SP2L_weekly_backtest_report_2026-09-20_trades.csv` (derived view, gitignored)

## Phase 7 — Tests

- pytest: 36 passed (new: `tests/test_backtest_weekly_journal.py`)
- `npm test` (vitest): 124 passed
- `npm run build` (`tsc --noEmit`): clean

## Safety statement

- No strategy rules, geometry, or parameters were changed or optimized.
- The report layer consumes an existing research artifact; it generates no
  signals and cannot place orders (no MT5 import in the reporting path).
- `LIVE_TRADING_ENABLE=false` everywhere.
- Telegram delivery remains MOCK/NOT_CONFIGURED; no destination was created
  or guessed.
