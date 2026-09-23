# SP2L Live Session Snapshot — 2026-09-23

Branch: `research/sp2l-f13-demo-forward-slfixed-2026-09-21`
Scope: **research/infrastructure only.** No SP2L strategy rule, P-Gap
definition, AB=CD logic, Leg1/Leg2 assumption, or SL/TP semantics was touched
anywhere in this snapshot. Live trading remains gated (`LIVE_TRADING_ENABLE`
defaults false; execution is DEMO-account-only).

---

## 1. What today was about

The multi-symbol SP2L forward test on the OtetGroup demo account
(812930) moved from "runs and reports" to a **fully self-declaring,
self-healing session**:

- symbol selection and per-symbol volume became configuration,
- every Telegram notification states the session's execution mode,
- stale pending limit orders expire and announce themselves,
- Telegram credentials no longer depend on shell environment variables,
- the 10-symbol replay backtest established which symbols even produce
  SP2L signals under the frozen parameters.

## 2. Commits (chronological, this branch)

| Commit | Subject |
|---|---|
| `691adf9` | merge F13 lifecycle fix with MT5 terminal path support |
| `95cb948` | F13 forward: add MT5 terminal auto resolver foundation |
| `431c75f` | F13 persist Telegram config fallback loader |
| `22199f1` | F13 add forward risk validation gate |
| `24a7b74` | F13 add locked Telegram formatter |
| `39d08dc` | add MT5 history reconciliation helper for forward audit |
| `359eb6c` | fix: correct forward lifecycle exit telemetry and enforce research limit mode |
| `1b93547` | merge (remote sync) |
| `c0c7ed1` | research: forward watchdog, HTML result messages, daily summary, green suite |
| `f4be7f9` | research: configurable forward symbols, per-symbol volume, resolver hookup |
| `aeaf16d` | research: forward-test startup banner self-declares execution mode |
| `4470041` | research: pending-order expiry policy for forward-test limit orders |
| `d2ba72b` | research: execution-mode self-declaration in watchdog and daily summary |
| `d7f2846` | research: --banner-only flag for safe Telegram/banner verification |
| `05f03c8` | fix: BOM-tolerant telegram.json loader + machine-isolated credential tests |

## 3. Bugs found today and their fixes

### 3.1 `SP2L-TEST` market fills destroyed the 1R risk/reward
The multi-symbol runner declared `PENDING_LIMIT_RESEARCH` but never published
the order mode to the gateway, which silently defaulted to MARKET. The 15:05
gold fill on 2026-09-22 landed 1.02 above the theoretical entry while SL/TP
stayed theoretical: real risk 3.10, reward 1.06 → **R:R 0.34 instead of 1:1**.
Fix: `os.environ.setdefault("MT5_FORWARD_ORDER_MODE", ORDER_MODE)` (commit
`359eb6c`). Verified live: the session now places genuine limit orders.

### 3.2 Wrong exit message numbers (history-deal leak)
`history_deals_get(start, end, position=...)` **ignores the position filter
when a date range is passed** and returns the whole window's deals. The
volume-weighted "entry" was the mean of nine unrelated trades (4347.104
instead of 4325.61) → the TP'd trade messaged "−2043 pips". Fix: query by
position without a range, filter to the runner's magic, volume-weight, and
**defer exit notifications whose entry cannot yet be resolved** (never send a
wrong number; `n/a (unlinked)` instead) — commits `359eb6c` / `c0c7ed1`.
Reconstruction against the real position 61264742 matched the broker report
exactly: Entry 4325.61 / Exit 4326.67 / TAKE PROFIT / +106 pips / +1.06.

### 3.3 MT5 terminal not found (`-10003`) on non-default install
The terminal lives in `C:\Program Files\Otet Group MT5 Terminal\`, which the
MetaTrader5 package's default search never finds. The user's own
`mt5_terminal_resolver.py` was wired into both forward runners and the replay
backtester (`f4be7f9`); no `MT5_TERMINAL_PATH` env is needed anymore.

### 3.4 `config/telegram.json` BOM → silently NOT_CONFIGURED
PowerShell's `Set-Content -Encoding utf8` writes a BOM; the plain-utf8 JSON
read in `telegram_client.read_telegram_config` threw and returned
`(None, None)`, so a session with valid credentials on disk started without
Telegram. Fix: `utf-8-sig` (`05f03c8`). Four credential-path tests that only
passed because the local file was empty are now machine-isolated.

### 3.5 CLOSEONLY status re-check
Earlier finding reversed: with a live probe `XAUUSD.ecn` currently reports
`trade_mode=4` (**FULL**), as do EURUSD/BTCUSD and the index CFDs — the
symbol-level constraint is gone. Note the mapping that settles this for good:
**3 = CLOSEONLY, 4 = FULL** (an old probe test fixture had them swapped; fixed
in `c0c7ed1`). The four-layer execution safety gates are unchanged.

## 4. New capabilities (all research/infrastructure)

### 4.1 Symbol selection & per-symbol volume (`f4be7f9`)
- `SP2L_SYMBOLS="XAUUSD,GBPUSD,USTEC"` — default `XAUUSD,EURUSD,BTCUSD`;
  XAUUSD stays slot 1 (magic `MAGIC_BASE+index+1` follows list order).
- `SP2L_VOLUME_<BASE>` override — index CFDs on Otet have `volume_min=0.1`
  (US500/USTEC/DJ30); a 0.01 volume would be broker-rejected.
- Volume flows through signal messages, `ORDER_ATTEMPT` telemetry and the
  startup banner.

### 4.2 Execution-mode self-declaration (`aeaf16d`, `d2ba72b`)
Shared `execution_mode_line()` in runner and watchdog; every notification —
startup banner, watchdog started/DOWN/restarting/giving-up, nightly daily
summary — carries:

```
🟩 Execution: LIVE-DEMO        (both flags true; still DEMO-only)
🟨 Execution: DRY-RUN          (otherwise)
   LIVE_TRADING_ENABLE=<v> · ALLOW_REAL_EXECUTION=<v>
```

Flags are read from the notifying process's own environment — no outside
guessing (previously required reading process memory to tell which mode a
session had).

### 4.3 Pending-order expiry (`4470041`)
`SP2L_PENDING_TTL_MINUTES` (default 30, 0 disables): the runner cancels its
own unfilled BUY/SELL **limit** orders after TTL and announces the outcome
(`🟠 … EXPIRED` message + `PENDING_ORDER_EXPIRED` /
`TELEGRAM_PENDING_EXPIRED` events). Guards: own magic / tracked tickets only,
limit types only, DEMO account + both operator flags for a real cancel,
DRY-RUN never sends, idempotent via the per-ticket `EXPIRY_NOTIFIED` marker.
Positions, foreign/manual orders and SL/TP semantics are never touched.

### 4.4 `--banner-only` verification mode (`d7f2846`)
`python scripts/run_sp2l_author_replica_multi_symbol_forward_test.py
--banner-only` renders and sends the exact startup banner (shared
`_build_banner_text` helper — same text a real session sends), logs
`BANNER_ONLY_TELEGRAM`, exits 0/1 on Telegram success/failure, **without**
the scan loop or the single-instance lock. Complements
`scripts/telegram_diagnostic.py` (config-only, `--get-me` optional, never
messages the group).

### 4.5 Session infrastructure (`c0c7ed1` + `4470041` context)
- `scripts/forward_watchdog.py` — detached background supervisor: restarts
  the runner on exit, announces DOWN/🟠restarting/UP and give-up, keeps a
  pid file; `--stop` closes watchdog (+ runner via lock).
- Single-instance runner lock — a second runner is rejected (two runners
  would double every order).
- Nightly daily summary at 21:00 UTC (00:30 Iran) — signals/fills/W-L/net
  per symbol, from the day's event log, once per UTC day.

### 4.6 Telegram credentials without env (`431c75f`, `05f03c8`)
`config/telegram.json` (gitignored) now holds the bot token + chat id; env
vars still win if set. The session therefore survives reboots without
re-entering credentials — only the two execution flags remain session-scoped.

## 5. Multi-symbol replay backtest (`f4be7f9`, `artifacts/backtest-multi/`)

Frozen parameters on every symbol (P-Gap 1.0 price units, spike ×1.5,
MaxSL 10.0, TP 1R). Data: M1 straight from the Otet terminal, 2026-09-16 →
2026-09-23 UTC. `research_only: true, canonical: false` everywhere.

| Symbol | Bars | Signals | W/L/A | Win rate* | PF | Net R |
|---|---|---|---|---|---|---|
| **XAUUSD.ecn** | 6895 | **26** | 16/10/0 | **61.5%** | **1.60** | **+6.0** |
| **USTEC.c.ecn** | 6881 | **26** | 14/10/2 | 58.3% | 1.40 | +4.0 |
| **DJ30.c.ecn** | 6878 | **10** | 6/4/0 | 60.0% | 1.50 | +2.0 |
| US500.c.ecn | 6873 | 8 | 3/5/0 | 37.5% | 0.60 | −2.0 |
| EURUSD / GBPUSD / USDJPY / GBPJPY | ~7200 | **0** | — | — | — | 0 |
| BTCUSD.ecn | 7194 | **0** | — | — | — | 0 |
| XAGUSD.ecn | 6898 | **0** | — | — | — | 0 |

*decisive trades only. Total: 70 signals, 39 W / 29 L → **+10 R**.

**Key structural finding:** P-Gap is expressed in *price units* (1.0 on gold
= $1.00), so FX pairs (1.0 = 10,000 pip) and silver can never satisfy the
gap condition under the frozen parameter. Zero FX/silver/BTC signals are a
consequence of the frozen configuration, not a bug — and were **not**
"tuned away".

**Limitations (stated honestly):** one week only (70 signals is not
statistical proof); spread/commission not modeled (index spreads exceed
gold's); SL/TP ordering inside one M1 bar is unknowable from M1 data (the 2
USTEC AMBIGUOUS rows); data quality was verified (unique, chronological
timestamps; 1–16 weekly market gaps per symbol).

## 6. Session state at snapshot time (verified live)

- Runner pid 13384 + watchdog pid 9912, detached (survives window close);
  state file heartbeat every ~2–4 s.
- Process environment (read from memory, not assumed): `LIVE_TRADING_ENABLE=true`,
  `ALLOW_REAL_EXECUTION=true`, `MT5_FORWARD_ORDER_MODE=PENDING_LIMIT_RESEARCH`.
- Startup banner delivered `HTTP_200` (09:23:38 UTC) with the mode-declaring
  format; `pendingTtlMinutes: 30.0` recorded in the START event.
- Telegram: REAL mode from `config/telegram.json`; account 812930 (OtetGroup-MT5,
  DEMO); `XAUUSD.ecn / EURUSD.ecn / BTCUSD.ecn` watched.
- Test suite at snapshot: **pytest 99/99** (incl. 8 pending-expiry, 5
  execution-mode notices, 4 banner-only tests).

## 7. Operating the session

```powershell
# safe Telegram/banner test (works while a session runs; no lock, no loop):
.venv\Scripts\python.exe scripts\run_sp2l_author_replica_multi_symbol_forward_test.py --banner-only

# config-only check (no messages):
.venv\Scripts\python.exe scripts\telegram_diagnostic.py

# start (credentials persist in config/telegram.json; execution flags per session):
$env:LIVE_TRADING_ENABLE = "true"; $env:ALLOW_REAL_EXECUTION = "true"
Start-Process -WindowStyle Hidden -FilePath ".venv\Scripts\python.exe" -ArgumentList "scripts\forward_watchdog.py"

# stop:
.venv\Scripts\python.exe scripts\forward_watchdog.py --stop
Stop-Process -Id (Get-Content runtime\sp2l_multi_symbol_forward_runner.lock) -Force
Remove-Item runtime\sp2l_multi_symbol_forward_runner.lock
```

Env reference: `SP2L_SYMBOLS`, `SP2L_VOLUME_<BASE>`, `SP2L_PENDING_TTL_MINUTES`,
`SP2L_DAILY_SUMMARY_UTC_HOUR`, `SP2L_POLL_SECONDS`, `FORWARD_TEST_SECONDS`,
`FORWARD_WATCHDOG_MAX_RESTARTS`, plus the frozen research parameters
`SP2L_P_GAP_PRICE / SP2L_SPIKE_MULTIPLIER / SP2L_MAX_SL_DISTANCE / SP2L_TP_R /
SP2L_VOLUME`.

## 8. Natural next steps

- Longer replay window for the three proven symbols (~3.5 months of M1 are
  available) and spread-aware R accounting.
- Add expired-pending counts to the nightly summary.
- Retry `XAUUSD.ecn` order placement now that the symbol is FULL (the 03:30
  BTC `Invalid stops` reject predates the limit-mode fix).
- Consider a `--verify-chain` style end-to-end drill before any real-money
  discussion (which remains out of scope).
