# SP2L Telegram Reporting System — 2026-09-20

Branch: `research/sp2l-live-mt5-telegram-2026-09-19`

Deterministic daily/weekly/monthly reporting over the live journal with
Telegram delivery. **Reporting/infrastructure only**: no strategy rules were
changed, no geometry is defined or promoted, no trading signals are
generated, and live trading remains disabled (`LIVE_TRADING_ENABLE=false`).

## Architecture

The reporting layer extends the existing Python live-infrastructure modules
without duplicating them:

```
runtime/journal/{signals,trades}.jsonl      (existing append-only journal)
        │
        ▼
scripts/live_report_engine.py               (deterministic aggregation, pure)
        │  report dict (schema sp2l.live_report.v1)
        ▼
scripts/live_report_telegram.py             (fixed text templates + delivery log)
        │
        ▼
scripts/telegram_client.py                  (shared transport, extracted from
        │                                    scripts/live_mt5_gateway.py)
        ▼
runtime/journal/report_log.jsonl            (delivery audit: timestamp, type,
                                             Telegram response, success/failure)
```

- `scripts/telegram_client.py` — the pure HTTP Telegram sender extracted
  from the gateway. `live_mt5_gateway.telegram_send()` now delegates to it;
  gateway behavior is unchanged and its tests still pass. The report layer
  reuses the same client and the same `TELEGRAM_BOT_TOKEN` /
  `TELEGRAM_CHAT_ID` environment variables.
- `scripts/live_report_engine.py` — deterministic report engine. Pure
  functions of (journal records, explicit period bounds, explicit
  configuration). Rows are sorted by `(timestamp, signal_id, deal_id)` so
  JSONL record order cannot change results; floats are rounded only at the
  schema boundary (R: 4 dp, pips: 2 dp); missing inputs render as `null` /
  `n/a`, never invented substitutes.
- `scripts/live_report_telegram.py` — formatter layer with fixed message
  templates per report type; every send attempt is appended to
  `runtime/journal/report_log.jsonl`.
- `scripts/live_report_scheduler.py` — deterministic due-at decisions (see
  below).
- `scripts/run_sp2l_report.py` — CLI runner that builds, renders, exports
  (JSON/CSV) and optionally sends one report.
- `scripts/live_journal.py` — extended with `REPORT_LOG`
  (`runtime/journal/report_log.jsonl`), `record_report()` and a
  `report_log.csv` view in `export_csv()`.

## Report schema (`sp2l.live_report.v1`)

Canonical JSON (sorted keys) with sections:

- `schema`, `report_type` (`daily|weekly|monthly`), `generated_at_utc`
- `period`: `start_utc`, `end_utc` (half-open `[start, end)`),
  `session_timezone`, `basis`
- `signals`: `total`, `win`, `loss`, `ambiguous`, `duplicates_rejected`
- `performance`: `net_pips`, `net_r`, `profit_factor`, `win_rate_pct`,
  `max_drawdown_r`, `closed_with_r`, `closed_missing_r`, `pips_basis`
- `execution`: `open_trades`, `closed_trades`, `dry_run_trades`,
  `execution_failed`, `broker_reconciliation_status`
  (`RECONCILED | PARTIAL | NOT_RUN | NO_DATA`)
- `system`: `geometry_status` (config echo), `live_trading_status`
  (config echo), `journal_source`
- `determinism`: input/period record counts, `unclassified_records`
- weekly additionally: `daily_breakdown`, `trade_list_summary`
- monthly additionally: `daily_breakdown`, `trade_list_summary`,
  `weekly_breakdown`, `equity_summary` (R-basis equity curve + drawdown)

Reporting classification (not strategy semantics): `WIN`/`LOSS` come from
`result` fields already recorded by the gateway or the MT5 reconciliation
process. `AMBIGUOUS` is a journal-state label meaning the journal does not
deterministically resolve the outcome (no CLOSED record, or a CLOSED record
whose result is not WIN/LOSS). The engine never infers fills.

`max_drawdown` is peak-to-trough on the cumulative-R curve of the sorted
closed trades starting at 0. R-basis only; no money amounts are invented.

## Scheduler behavior

`scripts/live_report_scheduler.py` answers "is a report due now?"
deterministically:

- **Daily** — due after the configured New York close on that session day
  (`REPORT_NY_CLOSE_HHMM`, default `17:00`), once per local day
  (reason `AFTER_NY_CLOSE`; `ALREADY_SENT` blocks a resend).
- **Weekly** — due on Friday after the close (reason
  `AFTER_FRIDAY_CLOSE`); the trading week is the half-open window
  `[previous Friday close, this Friday close)`.
- **Monthly** — due on the last Mon–Fri local day of the month after the
  close (reason `LAST_TRADING_DAY_AFTER_CLOSE`). This is an explicit
  weekday proxy: no broker holiday calendar is consulted. If holiday-aware
  scheduling is required, set `REPORT_PERIOD_BASIS=UNRESOLVED_*` and
  scheduling is blocked, not guessed.

Timezone/session policy follows
`docs/research/SESSION_TIMEZONE_CORRECTION_2026-09-05.md`:

- Journal timestamps are canonical UTC; no timestamp is shifted.
- Session day/close calculations convert through the IANA database with the
  configured zone (`REPORT_SESSION_TIMEZONE`, default
  `America/New_York` per the session policy document). DST is handled by
  the zone database, never by fixed offsets.
- The NY close time is an **explicit configuration input**, not an inferred
  broker conversion. `scripts/mt5_session_*` tooling exists to verify
  broker session metadata before trusting it.
- If the zone database is unavailable, or any config value starts with
  `UNRESOLVED`, due decisions return
  `UNRESOLVED:...` and **no report fires** instead of inventing a
  conversion.

Idempotency: callers pass the last-send instant (derived from
`report_log.jsonl`) and the same period cannot be sent twice.

## Configuration

Environment (see `runtime/live-trader.env.example`):

| Variable | Default | Meaning |
|---|---|---|
| `REPORT_SESSION_TIMEZONE` | `America/New_York` | IANA zone for session-day grouping and close calculation |
| `REPORT_NY_CLOSE_HHMM` | `17:00` | Explicit NY close time in the session timezone |
| `REPORT_SCHEDULE_BASIS` | `EXPLICIT_NY_CLOSE_1700_ET` | Provenance marker; any `UNRESOLVED_*` blocks scheduled sends |
| `REPORT_PERIOD_BASIS` | `EXPLICIT_PERIOD_BOUNDS` | Period provenance marker echoed into reports |
| `REPORT_PIP_SIZE` | *(empty)* | XAUUSD price units per pip. Supplied explicitly, never inferred (repo convention). Empty ⇒ pips reported `n/a` |
| `SP2L_GEOMETRY_STATUS` | `UNRESOLVED_FROZEN_GEOMETRY_GATE` | Echoed verbatim into the System section |
| `LIVE_TRADING_ENABLE` | `false` | Echoed verbatim; must stay `false` |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | *(empty)* | Shared with the gateway; delivery is logged either way |

`requirements-live.txt` now includes `tzdata` so the IANA database resolves
on Windows Python.

## Usage

```powershell
# Weekly report for the previous trading week (scheduler bounds), JSON artifact:
python scripts/run_sp2l_report.py --type weekly `
  --start 2026-09-11T21:00:00+00:00 --end 2026-09-18T21:00:00+00:00 `
  --json-out artifacts/SP2L_report_weekly_2026-09-14_2026-09-18.json

# Same, plus CSV of period trades, plus Telegram send + delivery log:
python scripts/run_sp2l_report.py --type weekly --start ... --end ... `
  --csv-out runtime/exports/reports/trades.csv --send
```

Without `--send`, nothing leaves the host. Without credentials, the attempt
is logged with `telegram_status=NOT_CONFIGURED` and `success=false`.

## Historical verification (2026-09-20)

- Weekly artifact for the previous trading week (2026-09-14 → 2026-09-18):
  `artifacts/SP2L_report_weekly_2026-09-14_2026-09-18.json` — zero records,
  consistent with the journal (journal recording started 2026-09-19).
- Verification weekly over `[2026-09-14, 2026-09-21)` covering all recorded
  journal activity: `artifacts/SP2L_report_weekly_2026-W38_verification.json`
  — 6 signals, 6 trades, 0 unclassified; cross-checked against the raw
  journal (`JOURNAL_CONSISTENCY_OK`).
- Test Telegram send executed via the CLI; delivery attempt logged to
  `runtime/journal/report_log.jsonl` with `success=false`,
  `telegram_status=NOT_CONFIGURED` (credentials are intentionally not
  configured in the repository environment; the send path and the logging
  contract are covered by offline tests with a mocked transport).
- CSV exports under `runtime/exports/reports/` (gitignored, derived view).

## Tests

`tests/test_live_report_engine.py`, `tests/test_live_report_telegram.py`,
`tests/test_live_report_scheduler.py` (pytest, offline):

- daily / weekly / monthly aggregation; empty-journal case; determinism
  (input order cannot change output); explicit pip-size contract;
- Telegram template sections, deterministic rendering, failure handling and
  delivery-log records (success, failure, not-configured);
- scheduler DST correctness (EDT 21:00Z vs EST 22:00Z), due/idempotency
  rules, weekly/monthly windows, env-driven configuration, invalid-time
  rejection, unresolved marking.

Results at time of writing: pytest 31 passed; `npm test` (vitest) 124
passed; `npm run build` (`tsc --noEmit`) clean.

## Example Telegram weekly report (verification window, real journal)

```
SP2L Weekly Report — RESEARCH
Trading Period: 2026-09-14T00:00:00+00:00 → 2026-09-21T00:00:00+00:00 (America/New_York)

Signals:
- Total signals: 6
- WIN count: 0
- LOSS count: 0
- AMBIGUOUS count: 6

Performance:
- Net pips: n/a (basis: EXPLICIT_PIP_SIZE)
- Net R: 0.0000
- Profit factor: n/a
- Win rate: n/a
- Max drawdown: 0.0000 R

Execution:
- Open trades: 0
- Closed trades: 0
- Broker reconciliation status: NOT_RUN

Daily breakdown (America/New_York):
- 2026-09-19: signals=5 win=0 loss=0 ambiguous=0 net_r=0.0000
- 2026-09-20: signals=1 win=0 loss=0 ambiguous=0 net_r=0.0000

Trade list summary:
- DRYRUN-20260919-001 BUY DRY_RUN result=AMBIGUOUS r=n/a pips=n/a
- DRYRUN-SELL-20260919-001 SELL DRY_RUN result=AMBIGUOUS r=n/a pips=n/a
- DRYRUN-20260919-002 BUY DRY_RUN result=AMBIGUOUS r=n/a pips=n/a
- NEXORA-TELEGRAM-DRYRUN-001 BUY DRY_RUN result=AMBIGUOUS r=n/a pips=n/a
- NEXORA-TELEGRAM-DRYRUN-002 BUY DRY_RUN result=AMBIGUOUS r=n/a pips=n/a
- DRYRUN-20260920-001 BUY DRY_RUN result=AMBIGUOUS r=n/a pips=n/a

System:
- Geometry status: UNRESOLVED_FROZEN_GEOMETRY_GATE
- Live trading status: DISABLED (LIVE_TRADING_ENABLE=false)
```

All six records are dry-run gateway test signals; the journal contains no
closed trades for the period, so the report truthfully shows zeros/`n/a`.

## Safety boundaries

- No SP2L strategy logic, geometry, P-Gap/AB=CD/Leg1/Leg2 definitions, fill
  semantics or entry/SL/TP rules were changed or defined.
- The reporting layer never generates BUY/SELL signals; it only summarizes
  journal records that already exist.
- `LIVE_TRADING_ENABLE` remains `false`; the report runner cannot execute
  orders (it never imports MT5 or the gateway execution path).
- Telegram remains a notification transport receiving already-computed,
  already-labelled research output (`SP2L … Report — RESEARCH`), per the
  research live-mode contract.
- Every Telegram delivery attempt is logged with timestamp, type, response
  and success/failure for auditability.
