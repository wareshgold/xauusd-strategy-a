# Batch 43 Result Snapshot — MT5 P-Gap Candidate Comparison — 2026-09-21

## Status
RESEARCH_ONLY / DESCRIPTIVE_ONLY

Canonical geometry was not changed. Live trading was not enabled.

## Dataset
`data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv`

## Candidate V1 parameters
- pressure_min: 10 candles
- pressure_max: 30 candles
- pause_len: 2 candles
- compression_factor: 0.75
- trend_body_factor: 1.5

These remain research hypotheses and are not source-confirmed P-Gap geometry.

## Observed counts
| Measure | Count |
|---|---:|
| Candidate V1 events | 1,755 |
| Existing 3-candle imbalance events | 7,402 |
| Overlap | 290 |
| Candidate-only | 1,465 |
| Imbalance-only | 7,112 |

The two observations are materially different event sets on this MT5 sample. Only 290 events overlap.

## Interpretation boundary
This result is descriptive. It does not establish that Candidate V1 is more source-aligned, and it must not be used to select or optimize canonical P-Gap geometry.

The large candidate-only and imbalance-only populations justify the next forensic step: inspect representative candle-level events from each population against the archived source concept of pressure → pause/compression → trend-bar → continuation expectation.

## Next step
Commit/push the generated JSON artifact:
`artifacts/research/SP2L_PGAP_CANDIDATE_MT5_COMPARISON_2026-09-21.json`

Then perform candle-level forensic sampling of candidate-only, imbalance-only, and overlapping events. The forensic report remains descriptive and source-aligned; no threshold tuning, performance optimization, or canonical promotion.

## Reproducibility
```powershell
python scripts\research\compare-pgap-candidate-mt5.py --csv data\mt5-acquisition\xauusd_ecn_m1_2026-08-21_2026-09-18.csv
```

Observed output:
`artifacts/research/SP2L_PGAP_CANDIDATE_MT5_COMPARISON_2026-09-21.json`
