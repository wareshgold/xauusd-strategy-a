# SP2L Batch43 — Candle-Level P-Gap Forensic Sampling — 2026-09-21

## Status
**RESEARCH-ONLY / DESCRIPTIVE / NON-CANONICAL**

Batch43 established that the Candidate V1 developmental detector and the existing three-candle imbalance observation produce materially different event populations. This step samples actual MT5 M1 candle windows from three populations:

1. candidate-only;
2. overlap;
3. imbalance-only.

The purpose is forensic comparison against the source-confirmed P-Gap concept:

**10–30 candles of trend pressure → pressure pauses/compression → trend-bar → continuation expectation.**

## Rules
- No trade outcomes.
- No threshold optimization.
- No parameter selection.
- No canonical geometry change.
- No production signal generation.
- Existing imbalance remains an implementation/research observation, not P-Gap.
- P-Gap executable OHLC/index geometry remains unresolved.

## Reproducibility
Run:

```powershell
python scripts\research\forensic-pgap-candle-samples.py --csv data\mt5-acquisition\xauusd_ecn_m1_2026-08-21_2026-09-18.csv
```

The script writes:
`artifacts/research/SP2L_BATCH43_PGAP_CANDLE_FORENSICS_2026-09-21.json`

It deterministically recomputes both detectors and selects evenly spaced samples from each population, retaining a ±6-candle forensic window.

## Interpretation
The artifact is evidence for comparing detector behavior only. A sampled event can be visually consistent or inconsistent with the source concept, but that observation does not by itself define the missing canonical OHLC formula, candle index, bullish/bearish mirror, or classification boundary.

## Next gate
Use the sampled windows for source-aligned forensic review. Only independently source-confirmed geometry may move Frozen Geometry toward READY.
