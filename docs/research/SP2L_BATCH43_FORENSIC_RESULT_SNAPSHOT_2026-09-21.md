# SP2L Batch43 — Forensic Result Snapshot — 2026-09-21

## Status

Batch43 candle-level forensic sampling completed and archived.

Branch: `research/sp2l-batch43-pgap-mt5-candidate-comparison-2026-09-21`

Research commit: `aaf20ae`

## Dataset

`data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv`

## Population comparison

| Population | Count |
|---|---:|
| Candidate V1 | 1,755 |
| Existing three-candle imbalance | 7,402 |
| Overlap | 290 |
| Candidate-only | 1,465 |
| Imbalance-only | 7,112 |

Candidate V1 therefore identifies a materially different event population from the existing imbalance observation.

## Forensic sample artifact

`artifacts/research/SP2L_BATCH43_PGAP_CANDLE_FORENSICS_2026-09-21.json`

The artifact contains deterministic evenly-spaced samples with a +/-6 candle window for candidate-only, overlap, and imbalance-only populations.

## Research interpretation

- The Candidate V1 population is structurally narrower than the generic three-candle imbalance population.
- Candidate-only examples contain the intended research-state ingredients: bounded pressure duration, a compression/pause condition, and a directional expansion candle.
- The samples are descriptive evidence only; they do not establish that Candidate V1 is the teacher's P-Gap geometry.
- The existing imbalance observation remains non-canonical and must not be substituted for source-confirmed P-Gap geometry.
- No threshold, endpoint, candle index, fill rule, or execution rule is promoted by this batch.
- Frozen Geometry remains **BLOCKED**.
- Fresh Holdout remains **BLOCKED**.

## Next gate

The next research step is a source-alignment forensic review of the sampled candle structures against the archived teacher evidence. The purpose is to identify which observable structural properties are actually supported by the source, without tuning Candidate V1 or promoting it to canonical geometry.

No production BUY/SELL logic is changed by Batch43.
