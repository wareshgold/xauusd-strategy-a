# Batch 43 — MT5 P-Gap Candidate Comparison

Research-only harness committed at `scripts/research/compare-pgap-candidate-mt5.py`.

Run after pulling the branch:

```powershell
python scripts\research\compare-pgap-candidate-mt5.py --csv data\mt5-acquisition\xauusd_ecn_m1_2026-08-21_2026-09-18.csv
```

Output:
`artifacts/research/SP2L_PGAP_CANDIDATE_MT5_COMPARISON_2026-09-21.json`

The report compares:

- P-Gap Candidate V1 event count;
- existing three-candle imbalance observation count;
- overlap;
- candidate-only events;
- imbalance-only events.

It does **not** calculate trading performance and does not promote either detector to canonical geometry.

Important: the candidate thresholds are research hypotheses, not source-confirmed rules.
