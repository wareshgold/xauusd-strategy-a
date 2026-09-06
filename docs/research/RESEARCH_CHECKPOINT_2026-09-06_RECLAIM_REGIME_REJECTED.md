# Research Checkpoint — 2026-09-06

## Branch
`research/ny-sell-preentry-temporal-replication`

## Base commit
`a4607b946df1c0736589aa2b3d54224b20f50c80`

## Current research conclusion
The NY SELL reclaim-regime hypothesis was tested descriptively on the locked DEV+VAL universe only.

Command:
`pnpm run research:ny-sell-reclaim-regime-hypothesis`

Result:
- N=29, DEV=15, VAL=14, FRESH=LOCKED
- Fixed ex-ante geometric boundary = 0.5
- ALL: AvgR +0.692492, PF 2.338817
- NO_EXCEPTIONAL: AvgR -0.370744, PF 0.357377

Regimes:
- WEAK_BOTH: N=24, WR 41.67%, AvgR +0.847430, PF 2.452738, exceptional=3; excluding exceptional AvgR -0.446822, PF 0.329767
- MIXED: N=2, WR 50%, AvgR -0.416383, PF 0.167234
- STRONG_BOTH: N=3, WR 100%, AvgR +0.192232, no exceptional winners; sample is too small for promotion

Temporal behavior is unstable:
- WEAK_BOTH AvgR by DEV_H1 / DEV_H2 / VAL_H1 / VAL_H2 = -0.139783 / +2.678063 / +1.305466 / -0.409133
- STRONG_BOTH counts = 2 / 1 / 0 / 0

## Decision
REJECT reclaim regime as a trading rule.

Do NOT optimize the 0.5 boundary. Do NOT unlock Fresh. Do NOT modify Strategy A production logic.

The underlying reclaim features remain descriptive variables of interest because prior sensitivity analysis showed positive monotonic association after exceptional-winner removal, but N=29 is insufficient to establish an edge.

## Next research axis
Move away from reclaim thresholds/regimes. Investigate trigger-process / entry-timing / trigger-quality structure using fixed, ex-ante definitions and replication across the existing DEV/VAL data.

The next axis must answer whether the *way price reaches the reclaim trigger* contains stable information beyond the reclaim magnitude itself.

Required discipline:
1. No Fresh access.
2. No threshold mining.
3. No optimization against DEV/VAL.
4. No new trading rule unless a candidate survives descriptive replication first.
5. Preserve chronological temporal checks: DEV_H1, DEV_H2, VAL_H1, VAL_H2.
6. Explicitly test dependence on exceptional winners.
7. Stop/close the axis if evidence is unstable or sample sizes are inadequate.

## Freebuff handoff intent
Freebuff must treat this checkpoint as a research investigation, not a request to invent a strategy. It should inspect the existing analyzers/detectors and implement the smallest auditable next-stage analysis, run it locally, report compact metrics, and only then propose the next step.
