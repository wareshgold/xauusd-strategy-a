# SP2L Live Infrastructure Checkpoint — 2026-09-19

## Purpose

This checkpoint records the current state of the guarded MT5 + Telegram live-infrastructure work and the next research/execution gates.

## Repository / branch

- Repository: wareshgold/xauusd-strategy-a
- Branch: research/sp2l-live-mt5-telegram-2026-09-19
- Checkpoint date: 2026-09-19
- Strategy A canonical signal generation remains BLOCKED.

## Source / strategy safety boundary

The live gateway is an execution/notification shell only. It is NOT a canonical Strategy A signal engine.

The gateway must not infer or invent:
- P-Gap geometry
- AB=CD anchors or tolerance
- Leg 1 / Leg 2 equality
- fill semantics
- pending-order semantics
- unresolved execution rules

Frozen Geometry remains blocked. Backtest performance does not promote a research implementation into canonical production logic.

## MT5 connectivity verified

Local environment:
- Python 3.12.10
- MetaTrader5 package 5.0.6180
- openpyxl 3.1.5
- Terminal: Otet Group MT5 Terminal
- Company: Otet Group Ltd.
- Server: OtetGroup-MT5
- Symbol: XAUUSD.ecn
- MT5 connected: TRUE
- trade_allowed: TRUE
- trade_expert: TRUE
- Symbol visible/selected: TRUE
- Latest tested bid/ask: 4378.00 / 4378.22
- Volume minimum: 0.01
- LIVE_TRADING_ENABLE default: FALSE

## Gateway status

Verified dry-run path:
1. Gateway connected to MT5.
2. Artificial manually approved BUY signal was accepted.
3. Signal was journaled.
4. Exact market-order request was constructed.
5. No broker order was sent because LIVE_TRADING_ENABLE=false.
6. Signal was archived.
7. Market snapshots were recorded.

Test signal:
- signal_id: DRYRUN-20260919-001
- source: MANUAL_GATEWAY_TEST_ONLY
- direction: BUY
- symbol: XAUUSD.ecn
- volume: 0.01
- entry: 4378.22
- SL: 4370.00
- TP: 4394.66

This was an infrastructure test only, not a Strategy A production signal.

## Journal / Excel status

Raw append-only audit streams:
- runtime/journal/signals.jsonl
- runtime/journal/trades.jsonl
- runtime/journal/market_snapshots.jsonl

Current Excel export:
- runtime/exports/SP2L_Live_Trade_Journal.xlsx

Verified workbook sheets:
- Summary: 10 rows x 2 columns
- Signals: 2 rows x 11 columns
- Trades: 2 rows x 15 columns
- Market Snapshots: 91 rows x 8 columns

The default empty Excel worksheet was removed from the exporter.

Raw JSONL remains the audit source; XLSX is a derived analysis view.

## Code fixes completed

Recent live-branch fixes include:
- invalid zero/negative live signal price rejection
- persistent duplicate signal-id guard
- package-style gateway imports
- UTF-8 BOM acceptance for approved signal JSON
- nested journal-field serialization for Excel
- missing json import correction
- future-import ordering correction
- removal of stray replacement marker from Excel exporter
- removal of default empty Excel worksheet

Latest relevant exporter fix commit:
- 094bd499960a950580a47ca0ceb1a62325e8f656

## Current issue / observation

The command:

    Get-Content runtime/approved_signal.json

returned file-not-found.

This is expected after the prior consumed test signal was archived and the runtime approved-signal file is gitignored. It does NOT indicate that the gateway or journal is broken.

Do not commit runtime/approved_signal.json.

## PR #235 audit result — 2026-09-19

The existing guarded live-infrastructure work in PR #235 was audited before adding new functionality.

- PR #235 remains the primary live MT5 + Telegram implementation; no restart/rebuild is required.
- Existing verified scope includes MT5 connectivity, explicit APPROVED signal contract, dry-run execution, Telegram echo, append-only journals, Excel export, broker reconciliation, and duplicate-signal protection.
- A second, inferior duplicate gateway implementation (`scripts/mt5_live_gateway.py`) was removed from this branch so there is one authoritative gateway entry point: `scripts/live_mt5_gateway.py`.
- Duplicate-signal rejection now creates an auditable `DUPLICATE_REJECTED` signal-journal record and emits a Telegram acknowledgement instead of only printing to stdout.
- No Strategy A geometry or signal-generation logic was added or promoted.

## Next execution-infrastructure gates

1. Recreate a controlled manual APPROVED test signal with a NEW signal_id.
2. Run gateway with LIVE_TRADING_ENABLE=false.
3. Repeat the same signal_id and verify duplicate protection prevents a second execution attempt.
4. Verify duplicate event is journaled/auditable.
5. Test SELL dry-run using a separate signal_id.
6. Test gateway restart behavior and persistent duplicate protection.
7. Test MAX_OPEN_POSITIONS guard.
8. Verify Telegram delivery if credentials are configured locally.
9. Run MT5 journal reconciliation against broker history.
10. Keep live trading disabled until all dry-run gates pass and explicit human approval is given.

## Production Strategy A gate

Even if all infrastructure tests pass, production Strategy A auto-signals remain blocked until:

SOURCE RESOLUTION
-> SYNTHETIC FIXTURES
-> FROZEN GEOMETRY
-> DEV
-> UNTOUCHED VALIDATION
-> ROBUSTNESS/STABILITY
-> FRESH HOLDOUT
-> PRODUCTION

The live gateway may be production infrastructure, but it must not autonomously generate Strategy A BUY/SELL decisions before the canonical strategy gates are passed.

## Research journal objective

Every approved signal and execution outcome should remain traceable so later research can analyze:
- signal context
- execution outcome
- broker facts
- R-multiple
- win/loss
- market snapshot around the event
- repeated/duplicate attempts
- execution failures

Journal data can inform later research, but cannot itself redefine canonical Strategy A geometry.
