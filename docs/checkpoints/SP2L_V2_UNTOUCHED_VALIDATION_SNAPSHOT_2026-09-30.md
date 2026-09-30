# SP2L V2 Validation Snapshot — 2026-09-30

## Repository boundary
- Repository: wareshgold/xauusd-strategy-a
- Branch: research/sp2l-legacy-mirror-backtest-20260929
- Baseline commit before this snapshot: 8ed960f2
- Branch was synchronized with origin before the Untouched run.
- Snapshot purpose: freeze the research state after independent Untouched validation and before temporal-stability analysis.
- This snapshot does not promote any exit rule to canonical status.

## Research workflow state
SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION

Current state:
- Discovery: COMPLETE
- Untouched temporal validation: COMPLETE
- Current gate: TEMPORAL STABILITY / SUB-PERIOD ANALYSIS
- Canonical production decision: NOT REACHED

## Source / detector contract
- Detector: sp2l_strategy_a_v2_detector.py
- signal_geometry_unchanged: true
- initial_sl_unchanged: true
- P-Gap price: 1.0
- spike multiplier: 1.5
- max SL distance: 10.0
- Exit experiment mode: NON_CANONICAL_FORENSIC_EXIT_RESEARCH
- canonical: false

## Untouched window
- Start UTC: 2026-07-01T00:00:00+00:00
- End UTC: 2026-08-26T00:00:00+00:00
- End inclusive: false
- Symbol: XAUUSD.ecn
- M1 bars: 54,925
- All-hours population signals: 910
- Window verified from generated JSON metadata.
- Discovery starts at 2026-08-26T00:00:00Z, so the two validation windows do not overlap.

## Untouched results — ALL_MARKET_HOURS
| Variant | Signals | Decisive | WR | Net R | PF | Max DD | Max losing streak |
|---|---:|---:|---:|---:|---:|---:|---:|
| RR_1_NO_TRAIL | 910 | 909 | 68.4268% | +335.0R | 2.1672 | 9R | 7 |
| RR_2_NO_TRAIL | 910 | 908 | 46.9163% | +370.0R | 1.7676 | 13R | 9 |
| NO_TP_TRAIL_10P | 910 | 910 | 99.4505% | +538.1631R | 135.5408 | 1R | 1 |
| NO_TP_TRAIL_20P | 910 | 910 | 89.1209% | +429.5230R | 5.3829 | 5.3984R | 4 |
| NO_TP_TRAIL_30P | 910 | 909 | 74.3674% | +400.8261R | 2.7352 | 12.6279R | 9 |
| NO_TP_TRAIL_50P | 910 | 909 | 53.1353% | +379.8441R | 1.8938 | 22.0710R | 13 |

## Untouched results — LONDON_TO_NEW_YORK
- Entry session is IANA DST-aware: >= 08:00 Europe/London and <= 17:00 America/New_York.
- Signals: 566.

| Variant | Decisive | WR | Net R | PF | Max DD | Max losing streak |
|---|---:|---:|---:|---:|---:|---:|
| RR_1_NO_TRAIL | 566 | 69.6113% | +222.0R | 2.2907 | 4R | 4 |
| RR_2_NO_TRAIL | 566 | 47.3498% | +238.0R | 1.7987 | 8R | 8 |
| NO_TP_TRAIL_10P | 566 | 99.4700% | +344.0496R | 173.0248 | 1R | 1 |
| NO_TP_TRAIL_20P | 566 | 89.5760% | +262.5930R | 5.4507 | 2.9564R | 2 |
| NO_TP_TRAIL_30P | 566 | 76.1484% | +241.4861R | 2.8157 | 6.3339R | 4 |
| NO_TP_TRAIL_50P | 566 | 53.0035% | +230.4726R | 1.8697 | 12.6009R | 8 |

## Discovery comparison — same exit matrix
Discovery window: 2026-08-26 through 2026-09-25.

ALL_MARKET_HOURS:
- RR1: 66.8498%, +184R, PF 2.0166, 548 signals / 546 decisive.
- RR2: 45.0549%, +192R, PF 1.6400, 548 / 546 decisive.
- Trail10: 97.6277%, +407.2450R, PF 34.9371.
- Trail20: 86.4964%, +335.0673R, PF 5.6537.
- Trail30: 70.6204%, +222.1596R, PF 2.3885.
- Trail50: 51.0949%, +114.7741R, PF 1.4331.

LONDON_TO_NEW_YORK:
- RR1: 68.1957%, +119R, PF 2.1442, 329 signals / 327 decisive.
- RR2: 47.5610%, +140R, PF 1.8140.
- Trail10: 98.4802%, +253.3392R, PF 51.6678.
- Trail20: 86.3222%, +202.5837R, PF 5.6042.
- Trail30: 72.0365%, +143.4388R, PF 2.5763.
- Trail50: 52.8875%, +84.5785R, PF 1.5528.

## Mechanical audit
test_sp2l_v2_exact_window_exit_matrix.py passed all 7 fixtures:
- RR1 fixed TP
- RR2 fixed TP
- no-TP trailing activates on next bar
- no hidden TP in no-TP mode
- SELL no-TP trailing
- DST-aware London/New York session window
- session filter is entry-only

Audit status: PASS.

## Interpretation boundary
- RR1 shows similar win-rate behavior across the independent Discovery and Untouched periods.
- This is evidence of temporal reproducibility under the tested replay contract, not yet proof of a canonical trading edge.
- No exit variant is selected, ranked, or promoted by this snapshot.
- Trailing results remain non-canonical because their M1 replay semantics and intrabar ordering are not source-confirmed; same-bar SL/TP is explicitly AMBIGUOUS and m1 intrabar order is NOT_INFERRED.
- USD P&L excludes spread, commission, and swap; R is the primary research accounting unit.
- Next step is temporal stability/sub-period analysis with the same frozen detector and exit matrix, without parameter tuning or selection.

## Evidence artifacts
- Untouched JSON: artifacts/backtest-mt5-local/SP2L_V2_XAUUSD_EXITS_20260826_20260925_20260930T122900Z.json
- Untouched summary CSV: artifacts/backtest-mt5-local/SP2L_V2_XAUUSD_EXITS_20260826_20260925_20260930T122900Z.csv
- Runner: scripts/run_sp2l_v2_xauusd_exact_window_exit_matrix.py
- Mechanical tests: scripts/test_sp2l_v2_exact_window_exit_matrix.py
