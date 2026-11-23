# SP2L V3.1 XAUUSD RR4 / ACT40 / TRAIL40 — Recovery Registry

Registry created: 2026-11-23
Status: RECOVERED COPY IDENTIFIED; PRE-START SAFETY REVIEW INCOMPLETE.
Execution status: NOT STARTED.
MT5 orders submitted by this recovery task: NONE.
Canonical status: RESEARCH / DEMO FORWARD TEST ONLY; NOT CANONICAL OR PRODUCTION-APPROVED.

> This file is the recovery index. Start here next time; do not rediscover the runner by searching arbitrary folders or replacing it with a similarly named GitHub version.

## 1. Exact recovered location

Recovery SSD root:

`F:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-recovered-20261123`

Runner entry point:

`scripts\\run_sp2l_v3_1_xauusd_forward_test.py`

Python:

`.venv\\Scripts\\python.exe`

Expected operator terminal: PowerShell window 1, direct foreground invocation with Python `-u` so stdout/stderr remain visible. Do not use detached `Start-Process`.

## 2. Identity and SHA256 fingerprints

| File | SHA256 |
|---|---|
| `scripts/run_sp2l_v3_1_xauusd_forward_test.py` | `1E50F4AC41A397BB0FFA7DA7A2A2678E7066FCB1634DFD7190DA4D219812DE49` |
| `scripts/sp2l_v3_1_rr4_act40_config.py` | `9F46C547C17031AFC9E5169A124FDDEB44A6F5875118FC3321D5B6F81C8BC0AF` |
| `scripts/start_sp2l_v31_xauusd_forward.ps1` | `BC96C5B40D12333D806109A59003C05F75DD99D0522D56CD2D9550AAE3AE070F` |
| `scripts/run_sp2l_author_replica_multi_symbol_forward_test.py` | `889155AC4E4DF6E4CE8B21B566415747DC017E9FB3919544D701A1EF80C40EE3` |
| `scripts/live_mt5_gateway.py` | `AAB5204F8DEAC42355FC3EBB625768FEB022BE87BB5528051AF0C7404C2F8FE1` |
| `scripts/sp2l_v31_startup_recovery.py` | `EC89151A0E519A13724A780AEE700235333E977F432497104A65FAC55FB13ED4` |
| `artifacts/forward-test/SP2L_V3_1_XAUUSD_RR4_ACT40_FORWARD_EVENTS.jsonl` | `ED89E5E8F1FB7A0EB76F33CF12858CFAB1BC174A9E4D4292EF31B7DE509C0C25` |
| `runtime/sp2l_v3_1_xauusd_rr4_act40_forward_state.json` | `4C72F9F1C920ACE22DDDEA73B6577FC0669D4AF8FD299E2A0ABEC8C02C8104CF` |
| `runtime/sp2l_v3_1_xauusd_rr4_act40_trailing_state.json` | `3D11E547934B789CDC306ED61DD3BB2CD43C4B12C82E921A326190AEB948ECFF` |

These fingerprints identify the recovered local copy at the time of registration. Re-hash before any future start; if a hash differs, stop and investigate rather than silently replacing files.

## 3. Runtime and account target

- MT5 terminal: `C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe`
- Account login: `847788`
- Server: `OtetGroup-MT5`
- Account type: Demo (observed)
- Symbol: `XAUUSD.ecn`
- Magic: `26092301`
- Server UTC offset: `+2 hours` (explicit runner environment setting required)
- Observed pre-start state on 2026-11-23: connected, Algo Trading enabled, trade allowed, zero positions, zero pending orders.
- Duplicate runner process check: zero matching processes.
- Python: 3.12.10; MetaTrader5 5.0.6180; openpyxl 3.1.5; Flask 3.1.3; tzdata 2026.4.

## 4. Strategy/runtime settings recorded for this recovered candidate

- Version: `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101`
- Volume: 0.01
- TP_R: 4.0
- P-Gap: 1.0
- Spike multiplier: 1.5
- Max SL distance: 10
- Trail activation: 0.40 price units
- Trail distance: 0.40 price units
- `TRAIL_PIPS=4`
- `XAU_PIP_SIZE_PRICE=0.1`
- Initial SL anchor: `SPIKE_CANDLE_EXTREME_RESEARCH`
- Order mode: `PENDING_LIMIT_RESEARCH`
- Pending TTL: 30 minutes
- Session policy: `ALL_MARKET_HOURS`

These are recorded settings, not a declaration that unresolved source geometry, fill semantics, or execution behavior are canonical.

## 5. Preserved runtime state and backup

The original runtime state files were not cleared or rewritten. A pre-start copy was made on 2026-11-23 at:

`F:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-recovered-20261123\\artifacts\\prestart-backup-20261123-100411`

Backup SHA256:
- forward state: `4C72F9F1C920ACE22DDDEA73B6577FC0669D4AF8FD299E2A0ABEC8C02C8104CF`
- trailing state: `3D11E547934B789CDC306ED61DD3BB2CD43C4B12C82E921A326190AEB948ECFF`

The trailing state contains a historical ticket record for position 66441528, previously observed closed. Do not delete or reset it automatically. Inspect reconciliation behavior before changing state.

## 6. GitHub provenance warning

Repository: `wareshgold/xauusd-strategy-a`

Related historical snapshot:
`research/snapshots/SP2L_V3_1_RR4_ACT40_RUNNER_SNAPSHOT_20261101.md`

Related branch:
`research/strategy-a-v3-1-rr4-act40-20261101`

That older snapshot is useful historical provenance, but its recorded runner/config/shared-core hashes differ from this recovered local copy. Several nearby GitHub branches were compared and did not match the recovered files. Therefore:
- Do not overwrite this recovered folder with files from a similarly named branch.
- Do not claim the recovered files are byte-identical to the old GitHub snapshot.
- Preserve this local copy and its SHA256 fingerprints as the current recovery target until a full source match is proven.

## 7. Mandatory blockers before next start

1. Add and test an explicit account-login allowlist for login `847788` at every broker mutation boundary, including pending entry submission and trailing SL modification. Current inspected code enforces Demo mode but does not pin the login; trailing SL modification also needs the same account guard.
2. Re-check MT5 account/server/symbol, Algo Trading, tick freshness and explicit server offset immediately before start.
3. Inspect startup recovery against the preserved state. Do not reset state to make startup pass.
4. Run Telegram configuration/delivery readiness diagnostic without exposing token/chat values. The runner contains startup, order and lifecycle notification paths, but successful delivery has not yet been verified for this recovered copy.
5. Re-hash all critical files and confirm no duplicate runner.
6. Obtain explicit operator go-ahead after the above checks.

## 8. Execution flags and visible-log launch convention

The wrapper defaults `LIVE_TRADING_ENABLE=true` and `ALLOW_REAL_EXECUTION=true`. These flags enable actual order submission on the Demo account; this is not dry-run mode. The gateway currently blocks non-Demo accounts, but the explicit login pin is still a required blocker.

After all blockers are resolved and the operator explicitly approves, run in PowerShell 1 (foreground, live logs):

```powershell
$root = "F:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-recovered-20261123"
$env:SP2L_PENDING_SERVER_OFFSET_HOURS = "2"
$env:MT5_TERMINAL_PATH = "C:\\Program Files\\Otet Group MT5 Terminal\\terminal64.exe"
$env:LIVE_TRADING_ENABLE = "true"
$env:ALLOW_REAL_EXECUTION = "true"
Set-Location "$root\\scripts"
& "$root\\.venv\\Scripts\\python.exe" -u "$root\\scripts\\run_sp2l_v3_1_xauusd_forward_test.py"
```

Do not launch detached. Keep the PowerShell window open to observe logs. Do not run this command until the mandatory blockers above are resolved.

## 9. Current status at registration

- Runner process: NOT RUNNING.
- Runner started by this recovery task: NO.
- MT5 orders sent by this recovery task: NO.
- Telegram test message sent by this recovery task: NO.
- Login pin patch: NOT YET APPLIED.
- Telegram delivery readiness: NOT YET VERIFIED.
