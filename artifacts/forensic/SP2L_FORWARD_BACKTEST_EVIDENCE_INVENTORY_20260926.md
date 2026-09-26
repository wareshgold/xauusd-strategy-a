# SP2L Forward/Backtest Evidence Inventory — 2026-09-26

## Purpose

Research/forensic checkpoint only. This document records what is currently auditable from GitHub before the Monday open-market capture. It does not promote geometry, fill semantics, session rules, or execution rules.

## F13 branch inventory

Branch: `research/sp2l-f13-demo-forward-slfixed-2026-09-21`

The branch contains historical/research backtest artifacts, including:

- `artifacts/backtest-multi/SP2L_replay_XAUUSD_ecn_2026-09-16_2026-09-23.json`
- `artifacts/backtest-multi/SP2L_multi_symbol_replay_summary_2026-09-16_2026-09-23.json`
- `artifacts/backtest-multi/SP2L_fixed_sltp_matrix_full_history.json`

The expected raw forward event stream was **not found** on this branch at:

- `artifacts/forward-test/SP2L_AUTHOR_REPLICA_FORWARD_EVENTS.jsonl`

The expected point-in-time local backtest exports were also not found at:

- `artifacts/backtest-mt5-local/SP2L_MT5_LOCAL_MULTI_SYMBOL_20260926T051426Z.json`
- `artifacts/backtest-mt5-local/SP2L_MT5_LOCAL_MULTI_SYMBOL_20260923T105704Z.json`

Therefore no candidate-level forward/backtest reconciliation is run from fabricated or reconstructed data.

## Auditable XAUUSD replay snapshot

Source artifact: `SP2L_replay_XAUUSD_ecn_2026-09-16_2026-09-23.json`

- source: MetaTrader5 `copy_rates_from`
- research parameters: P-Gap 1.0, spike multiplier 1.5, max SL 10.0, TP 1R
- raw returned bars: 10,081
- filtered bars in requested interval: 6,895
- unique timestamps: true
- chronological: true
- gaps: 4
- detected signals: 26
- wins: 16
- losses: 10
- ambiguous: 0
- decisive win rate: 61.538%
- total R: +6
- profit factor: 1.60

This is a **research replay snapshot**, not a canonical performance claim. Its own metadata states that historical MT5 timestamp mapping remains unresolved.

## Important interpretation

The 61.538% result is materially different from the earlier four-week author-replica stability headline (~66.9% at the baseline configuration). This difference is not being interpreted as a strategy degradation or improvement.

The current evidence shows that the measurement universe and artifact generation path matter:

1. different date windows;
2. different data acquisition/replay artifact;
3. session/eligibility handling differs across research runners;
4. MT5 timestamp semantics remain unresolved for open-market evidence;
5. forward execution/fill semantics remain research-only.

Consequently, the correct next action is reconciliation of identical candidate identities and raw levels, not parameter tuning.

## Fixed-SL/TP experiment

`SP2L_fixed_sltp_matrix_full_history.json` is explicitly marked research-only and canonical=false. It uses synthetic fixed symmetric SL/TP widths and therefore cannot be used to redefine the Strategy A SL rule. Its results are retained only as sensitivity evidence.

## Current gate status

| Gate | Status |
|---|---|
| Shared detector parity | PASS |
| Closed-market MT5 API response | PASS |
| Internal tick/bar ordering | PASS |
| Open-market freshness | BLOCKED until Monday |
| Open-market timestamp semantics | BLOCKED until Monday |
| Forward continuous polling proof | NOT PROVEN |
| Candidate-level forward/backtest reconciliation | BLOCKED by missing raw forward artifact |
| Session eligibility parity | UNRESOLVED |
| Fill/execution semantics | UNRESOLVED |
| Canonical geometry | BLOCKED |
| Production readiness | NOT READY |

## Monday 2026-09-28 evidence target

The minimum decisive capture is:

`wall_clock_utc -> newest_bar_raw_time -> tick_raw_time -> detector_candidate -> forward_visibility -> order_state -> fill_state -> lifecycle`

No timezone normalization, tolerance, geometry change, session change, or execution rule will be introduced before that evidence exists.
