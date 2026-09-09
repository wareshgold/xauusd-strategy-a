# SP2L G34 — Data Splits and Trade Clustering

Date: 2026-09-09
Branch: `research/sp2l-data-splits-clustering-g34-2026-09-09`

## Purpose

Add strategy-neutral research infrastructure in parallel with unresolved source-geometry work. This gate does not freeze or implement Strategy A geometry.

## Dataset split contract

`research/engine/splits.py` defines a chronological three-way partition:

1. `DEV` — development research only.
2. `VAL` — validation after the specification is frozen.
3. `FRESH_HOLDOUT` — final untouched period, not used for tuning or interpretation before the preceding gates pass.

Default proportions are 60% / 20% / 20% by elapsed timestamp span. No shuffling is permitted. The split boundaries are explicit and testable.

This is an infrastructure default, not a claim that these proportions are optimal or source-derived.

## Trade clustering

`research/engine/clustering.py` groups trades by entry-time proximity using an explicit research parameter (`max_gap_minutes`, default 30). It reports cluster count, mean size, maximum size, and boundaries. This is descriptive only and must not become a Strategy A entry/session filter.

The same module summarizes MAE/MFE values when the neutral backtest layer has supplied them as trade metadata. Missing excursion fields remain missing; no synthetic values are imputed.

## Gate status

- SOURCE RESOLUTION: semantic pass / critical geometry unresolved.
- SYNTHETIC FIXTURES: ongoing/pass for covered hypotheses.
- FROZEN GEOMETRY: BLOCKED.
- DEV / VAL / ROBUSTNESS / FRESH HOLDOUT / PRODUCTION: LOCKED for Strategy A claims.

G34 therefore adds only reusable, strategy-neutral infrastructure. It does not authorize BUY/SELL generation, optimization, or validation claims for Strategy A.
