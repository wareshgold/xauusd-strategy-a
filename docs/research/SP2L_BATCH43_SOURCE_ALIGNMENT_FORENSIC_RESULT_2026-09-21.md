# SP2L Batch43 — Source-Alignment Forensic Result — 2026-09-21

## Execution status

The source-alignment forensic script was executed locally against:

\`data/mt5-acquisition/xauusd_ecn_m1_2026-08-21_2026-09-18.csv\`

Command completed successfully and produced:

\`artifacts/research/SP2L_BATCH43_SOURCE_ALIGNMENT_FORENSICS_2026-09-21.json\`

Population counts reproduced exactly:

| Population | Count |
|---|---:|
| Candidate V1 | 1,755 |
| Existing three-candle imbalance | 7,402 |
| Overlap | 290 |
| Candidate-only | 1,465 |
| Imbalance-only | 7,112 |

## Evidence interpretation

The execution confirms that the forensic partition is deterministic and reproducible on the local MT5 dataset.

It does **not** establish that Candidate V1 is the teacher's P-Gap.

The source audit confirms the following structural concepts:

- 10–30 candles of trend pressure
- pressure pauses/compression
- trend-bar after the pause
- continuation context

Candidate V1 also contains implementation-specific parameters:

- pause length = 2
- compression factor = 0.75
- trend-body factor = 1.5

Those parameters remain **implementation choices**, not source-confirmed rules.

The forensic measurements are therefore evidence about what Candidate V1 contains, not evidence that its numerical boundaries are canonical.

## Gate decision

**NO GEOMETRY PROMOTION.**

- Source Resolution: PARTIAL
- P-Gap concept: SOURCE-CONFIRMED
- P-Gap executable geometry: UNRESOLVED
- Frozen Geometry: BLOCKED
- Fresh Holdout: BLOCKED
- Production: BLOCKED

No outcome statistics, optimization, or trading decision is introduced by this batch.

## Next step

The next gate is not parameter tuning.

The next research task is to resolve missing source evidence for executable P-Gap geometry:

1. OHLC endpoints
2. candle indexing
3. bullish/bearish mirror
4. exact trend-bar semantics
5. deterministic compression boundary
6. gap formula/type binding

Until those are source-resolved, Candidate V1 remains research-only.
