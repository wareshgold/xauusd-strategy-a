# SP2L V3 Session Snapshot — 2026-10-01

Session record for the 2026-10-01 forward-test day: startup-crash fix, trade
forensics, costed exit matrix with walk-forward validation, live switch from
RR1/TRAIL10 to RR2/TRAIL4, and the dedicated backtest of the live settings.

- Branch: `research/sp2l-strategy-a-v3-1-monitoring-20261001`
- Remote: `https://github.com/wareshgold/xauusd-strategy-a.git`
- Account: 812930 (OtetGroup-MT5, DEMO), symbol `XAUUSD.ecn`, magic `26092201`
- Host timezone UTC+3:30; broker server UTC+3 (strict offset check passes)

---

## 1. Startup crash fix (offset-before-init)

The V3 wrapper computed the session cutoff with `mt5_server_offset_strict()`
*before* `_original_main()` initialized MT5, so every start failed
(`Invalid offset` fail-closed path). Fixed by resolving the cutoff lazily on
first use via `_session_cutoff_epoch()` + `cutoff_cache` inside `_v3_main()`.
Committed in `f42f20cd` (with `.gitignore` additions for runtime locks/state).

Related earlier same-day fixes: `d78cf481` (trailing broker-stop validation +
retry-spam dedupe, one attempt per ticket per completed bar),
`80822b27` (server-timestamp cutoff), `3497b8d6`, `652559c4`, `6e161373`.

## 2. Forward-test trade forensics (evidence: events jsonl + terminal journal)

Terminal journal: `%APPDATA%\MetaQuotes\Terminal\915A84104ED5196B12929C08F8F242A6\logs\20261001.log`

### Trade #62410652 — BUY 4162.97, filled 07:35:58 UTC
- Pre-fix runner spammed 30× `TRAIL_UPDATE` (target 4163.89) between
  07:36:00–07:36:58 UTC, all rejected `retcode 10016 Invalid stops` (target
  was above the already-retraced bid). Journal: `failed modify ... [Invalid stops]`.
- 11:10:52 local (07:40:52 UTC): **native MT5 trailing stop 100 points
  (=$1.00) was placed on the position from the terminal UI**
  (`Trailings ... trailing stop 100 point(s) on #62410652 ... placed`).
- 11:12:38 local: native trailing moved SL 4154.35 → **4162.97 (breakeven)**.
- 11:12:41 local: stopped out at `[sl 4162.97]`, fill 4162.91 → **−$0.06**
  instead of the original −$8.66 full SL.
- No runner process sent that SLTP (no `TRAIL_UPDATE` logged; the only
  `TRADE_ACTION_SLTP` code path is the V3 wrapper). Attribution: manual/native
  terminal-side action. Do NOT run native trailing and code trailing on the
  same position — they compete.

### Trade #62417157 — BUY 4161.56, filled 08:28:32 UTC (the "SL hit, never trailed" case)
- Max favorable high since entry = 4162.35 (**+0.79 < 1.0 trail threshold**);
  trailing activates only after ≥$1.0 favorable move on a *completed* M1 bar.
- Price reversed within 2 minutes; original SL 4156.24 hit at 08:30:27 UTC →
  **−$5.36**. Expected behavior by design, not a bug (matches backtest: losers
  that never reach the trail threshold lose the full SL).

## 3. Costed exit matrix + walk-forward (new script)

`scripts/run_sp2l_v3_xauusd_exit_matrix_costed.py` — same frozen population as
the uncased matrix (1522 signals, 2026-07-01→2026-10-01, 90637 M1 bars) plus:

- **Costs:** full spread 0.20 per trade (live observed 0.18) + slippage 0.05 on
  stop-type exits only (live worst observed 0.06); TP fills exact.
- **Walk-forward:** TRAIN = Jul+Aug, VALIDATE = Sep (signal_time_utc frame).

Artifact: `SP2L_V3_EXIT_MATRIX_COSTED_3M_20261001T093445Z.*`
(JSON SHA256 `e60c989a3241ec9eaed00b0f310cc6111663862181e3505f742158c75ba4718c`)

| variant | net R | PF | WR% | train R | validate R | validate PF |
|---|---|---|---|---|---|---|
| RR2_TRAIL3 | 467.4 | 10.71 | 87.6 | 322.7 | +144.7 | 8.10 |
| **RR2_TRAIL4** | **409.1** | **6.82** | **84.4** | **288.3** | **+120.8** | **4.79** |
| RR2_TRAIL5 | 357.5 | 4.88 | 81.6 | 257.2 | +100.3 | 3.32 |
| RR1_TRAIL3 | 291.3 | 7.13 | 86.0 | 197.9 | +93.3 | 5.58 |
| RR1_TRAIL10 (old live) | 39.4 | 1.22 | 71.2 | 45.7 | **−6.4** | **0.92** |

Conclusions: cost model does not change the ranking; the old RR1/TRAIL10 live
config loses money out-of-sample (Sep PF 0.92) after costs; RR2/TRAIL4 was
selected as the best stability/performance balance (operator decision).

## 4. Live switch to RR2_TRAIL4

- `scripts/sp2l_v3_config.py` — **frozen baseline kept at RR1/TRAIL10**
  (restored; matrices/backtests with default module stay comparable).
- `scripts/sp2l_v3_rr2_trail4_config.py` — variant module: `TP_R=2.0`,
  `TRAIL_PIPS=4.0`, `VERSION=SP2L_V3_XAUUSD_RR2_TRAIL4_20261001`.
- `scripts/run_sp2l_v3_xauusd_forward_test.py` — imports the variant config;
  events/state → `SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl` /
  `sp2l_v3_xauusd_rr2_trail4_forward_state.json`.
- `scripts/sp2l_v31_monitor.py` — dashboard repointed to the RR2_TRAIL4 files.
- Forward runner restarted (operator): START 10:05:08 UTC with `tpR: 2.0`,
  Telegram `HTTP_200`, single-instance lock held, dashboard `:8790` HTTP 200.
- Note: `run_sp2l_v3_xauusd_balanced_forward_test.py` (RR2_TRAIL3 profile) is
  superseded — it monkey-patches `sp2l_v3_config`, which the forward wrapper no
  longer imports. Reviving it requires switching it to the variant module too.

## 5. Dedicated backtest of the live forward settings

`scripts/run_sp2l_v3_xauusd_backtest.py` now takes `--config-module` and names
outputs from `cfg.VERSION` (the old hardcoded `TRAIL10` name is gone).

Run: `--config-module sp2l_v3_rr2_trail4_config`
Artifact: `SP2L_V3_XAUUSD_RR2_TRAIL4_3M_20261001T101458Z.*`
(JSON SHA256 `5d9629a4c6a4923fff93b03f0e10d521b00e2e924968248bd9fbe95cdb4f3932`)

| view | signals | decisive | ambiguous | WR% | net R | PF |
|---|---|---|---|---|---|---|
| Backtest (no costs) | 1522 | 1455 | 67 | 96.2 | 527.3 | 10.42 |
| Matrix costed (same replay) | 1522 | 1455 | 67 | 84.4 | 409.1 | 6.82 |
| Matrix costed, Sep only (OOS) | — | — | — | — | +120.8 | 4.79 |

Population/decisive/ambiguous counts match the matrix exactly → replay logic is
consistent. Baseline comparison (same day, RR1/TRAIL10 backtest, no costs):
net R 131.7, PF 1.86, WR 87.0
(`SP2L_V3_XAUUSD_TRAIL10_3M_20261001T092854Z.*`).

## 6. Caveats / follow-ups

1. Tighter trail (0.4) + RR2 raise live friction vs backtest: unplaceable trail
   targets are now *deferred* (guard) instead of spammed, so live trailing can
   run looser than the model — expect some slippage vs these numbers.
2. Never mix native MT5 trailing (terminal UI) with the runner's trail.
3. Telegram START notification timed out once this session (transient).
4. Forward session is RESEARCH/DEMO only; no canonical production decision.

## 7. Artifact index

- `SP2L_V3_EXIT_MATRIX_COSTED_3M_20261001T093445Z_{.json,.csv,_SUMMARY.csv,_SNAPSHOT.md}`
- `SP2L_V3_XAUUSD_RR2_TRAIL4_3M_20261001T101458Z_{.json,.csv,_SNAPSHOT.md}`
- `SP2L_V3_XAUUSD_TRAIL10_3M_20261001T092854Z_{.json,.csv,_SNAPSHOT.md}` (baseline)
- `../forward-test/SP2L_V3_XAUUSD_RR2_TRAIL4_FORWARD_EVENTS.jsonl` (live session, point-in-time)
- Previous matrices/events retained unchanged for the evidence trail.
