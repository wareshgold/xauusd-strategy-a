# SP2L V3.1 Forward Forensic Milestone — 2026-11-08

## Purpose and operating boundary

This is the durable checkpoint for the local V3.1 forward forensic investigation. It records the evidence already processed, the conclusions that are supported, the open questions, and the exact next stage so work can resume without repeating the archive analysis.

- Strategy/runtime under observation: `SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101`
- Symbol: `XAUUSD.ecn`
- Magic: `26092301`
- Current posture: preserve the existing forward runner as an observation baseline.
- The private capture ZIP and generated JSON/CSV remain on the operator's PC. Do not upload them to GitHub or any cloud service.
- The analyzer is read-only: no MT5 connection, no runner/state edits, no order/SL/TP operations, and no BUY/SELL output.
- Do not restart, stop, or modify the active runner as part of this forensic work.

## Workflow checkpoint

| Stage | Status | Evidence / next action |
|---|---|---|
| Local archive acquisition | COMPLETE | Private ZIP processed on PC; ZIP CRC PASS. |
| Read-only forensic analyzer | IMPLEMENTED; local run completed | `scripts/sp2l_v31_forward_forensic.py`; local report and per-position CSV produced. |
| Synthetic fixtures | PENDING operator confirmation | Run pytest in isolated forensic worktree; do not claim passed until output is recorded. |
| First-pass broker reconciliation | COMPLETE WITH LIMITATION | 160 deals, 163 orders, 1,074 events. 43 history query failures / 43 unique targets; all 43 targets found in final order history. |
| First-pass closed-position accounting | COMPLETE, subject to lifecycle caveats | 80 positions with observed entry and exit; 50 wins, 30 losses; win rate 62.5%; net -29.21 account currency; PF 0.7334; average -0.37. |
| Exit/trailing descriptive split | COMPLETE | 79 SL-coded exits (49 positive, 30 negative; net -31.50); one CLIENT exit (+2.29). 47/47 recorded TRAIL_UPDATE events success. |
| Trailing-count association | COMPLETE, descriptive only | 0 updates: 39 positions, net -101.41, avg -2.60. 1 update: 35 positions, net +57.06, avg +1.63. 2 updates: 6 positions, net +15.14, avg +2.52. |
| Manifest verification | NOT VERIFIED | MANIFEST_VERIFIED=0, mismatches=0. Zero mismatches is not proof of verification; inspect manifest schema and implement exact parser before claiming integrity validation. |
| Detailed cohort diagnostics | NEXT | Analyze side, hold duration, volume, entry/exit price, per-position net, trailing-event timing and SL levels. Read only the local CSV/JSON. |
| Price-path diagnostics (MFE/MAE) | BLOCKED ON VALIDATED PRICE DATA | Requires synchronized tick/bar evidence and explicit data-quality checks. |
| V3 vs V3.1 counterfactual | BLOCKED | Requires frozen identical entries plus separately validated replay/fill assumptions. Do not infer fills. |
| Strategy or runner change | NOT AUTHORIZED BY THIS EVIDENCE | No V3 rollback, V3.2, ACT40/TRAIL40/RR4 change based solely on this sample. |

## Captured results (operator-provided local output)

Archive:
- ZIP SHA-256: `fbc1bb300df063bf30cb30204f14199a70c56011c395a79da81e832971c1199b`
- ZIP CRC: PASS
- Deals / orders / events: 160 / 163 / 1,074
- Closed positions: 80
- Wins / losses: 50 / 30
- Win rate: 62.5%
- Net account currency: -29.21
- Profit factor: 0.7334
- Average net per closed position: -0.37
- Exit reasons: CLIENT 1; SL 79
- Trail updates: 47; success 47; failed 0
- History query failures: 43; unique targets 43; found in final orders 43
- Manifest verified entries: 0; mismatches: 0
- Local report JSON: `artifacts/forensic/v31-local-20261108/v31_forward_forensic_report.json`
- Local positions CSV: `artifacts/forensic/v31-local-20261108/v31_closed_positions.csv`

Additional local cohort summary:
- SL exit cohort: 79 positions; 49 positive, 30 negative; net -31.50; average -0.40.
- CLIENT exit cohort: 1 position; positive; net +2.29.
- No recorded trailing updates: 39 positions; net -101.41; average -2.60.
- One recorded trailing update: 35 positions; net +57.06; average +1.63.
- Two recorded trailing updates: 6 positions; net +15.14; average +2.52.
- Five worst positions were all SELL/BUY mixed, SL-coded and had zero trailing updates; their combined net was -37.96.
- Five best positions were SL-coded and had one or two trailing updates.

## Interpretation boundaries

1. A broker exit reason of `SL` is not synonymous with a losing trade. In this sample 49 of 79 SL-coded positions are net positive.
2. The strong difference between positions with and without trailing events is an association, not causal evidence. Reaching a trailing event is conditional on the price path and may select trades that already moved favorably.
3. `TRAIL_UPDATE success=true` means the recorded modification request succeeded according to the runner event; it does not establish the economic quality of the trailing rule or prove every later broker-side state transition.
4. The 43 order-history lookup failures appear reconcilable because every target exists in final order history. This does not prove that every lifecycle transition was correctly handled at the time.
5. The net calculation sums broker deal `profit + commission + swap + fee` where present, grouped by `position_id`. Treat account currency as the MT5 account currency. Validate lifecycle completeness, especially partial closes and INOUT/reversal records, before using this as a definitive accounting baseline.
6. `MANIFEST_VERIFIED=0` means the manifest was not successfully verified by the current parser. Do not call the archive manifest-verified.
7. No MFE/MAE, initial-risk R-multiple, causal trailing effect, or same-entry V3 counterfactual has been established.

## Next execution stage — local PC only

Use the already-created isolated worktree:
`D:\Mirzaei\Private\1\xauusd-strategy-a-v31-local-forensic-20261108`

Use the existing local CSV:
`D:\Mirzaei\Private\1\xauusd-strategy-a-v31-local-forensic-20261108\artifacts\forensic\v31-local-20261108\v31_closed_positions.csv`

Produce a compact, clipboard-friendly cohort report, with no archive upload:
- BUY vs SELL: count, wins/losses, net, PF, average/median net.
- Trailing count 0 / 1 / 2+: same metrics, split further by side.
- Hold duration (exit UTC minus entry UTC): count, median, quartiles, net and win rate by duration buckets; define bucket boundaries explicitly in the report.
- Volume-in/out and partial-close flags; flag mismatched total entry/exit volume for review.
- Entry/exit price movement by side, without converting it into R or assuming pip/point semantics.
- Join each position's trailing timestamps and SL values from raw events only after confirming the actual event schema. Do not assume an event field name or infer missing SL values.
- List lifecycle anomalies (missing entry, missing exit, INOUT/reversal, volume mismatch, duplicate/partial deals) separately from the clean cohort.
- Reconcile totals back to the first-pass 80-position / -29.21 summary.

Before using any price-path data, identify its source, timezone, sampling coverage, gaps, and bid/ask semantics. No MFE/MAE until that validation is complete.

## Decision gate for tomorrow-morning handoff

A useful handoff means a reproducible, locally tested evidence package and a clear status—not a promise that a profitable or production-ready strategy can be delivered overnight.

Do not change or deploy runner parameters from this forensic sample. A V3.2 proposal requires a separate, explicit research hypothesis, isolated development, tests, and untouched validation. A live strategy decision remains human-controlled and requires the project's full evidence workflow.
