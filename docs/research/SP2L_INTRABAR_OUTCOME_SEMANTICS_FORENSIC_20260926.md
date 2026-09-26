# SP2L Intrabar Outcome Semantics Forensic Checkpoint — 2026-09-26

## Objective

Record the deterministic forensic analysis of ambiguous outcomes produced by the research-only MT5 local replay:

`artifacts/backtest-mt5-local/SP2L_MT5_LOCAL_MULTI_SYMBOL_20260926T124056Z.json`

This checkpoint addresses outcome-resolution ambiguity only. It does not define or promote canonical Strategy A geometry, P-Gap formula, fill semantics, or execution rules.

## Input replay

- Period: 2026-09-14 through 2026-09-25 UTC
- Symbol: XAUUSD -> XAUUSD.ecn
- Timeframe: M1
- Research geometry: pGap=1.0, spike=1.5, maxSL=10, tpR=1.0
- Canonical: false
- Signals: 53
- Decisive: 33
- Ambiguous: 19
- Data gap: 1

## Ambiguous decomposition

The 19 ambiguous outcomes are:

- 6 `BOTH_SL_TP_SAME_BAR`
- 13 `ENTRY_TP_SAME_BAR_ORDER_UNRESOLVED`
- 14 SELL
- 5 BUY

For all 19 ambiguous cases, the OHLC range makes TP price-feasible within the implicated bar.

Among them:

- 6 cases also make SL price-feasible within the same bar (5 SELL, 1 BUY).
- 13 cases have TP price-feasible but SL not price-feasible in that bar (9 SELL, 4 BUY).

The OHLC record does not establish the intrabar ordering required to determine whether entry occurred before TP, or whether SL occurred before TP when both are touched.

## Important semantic finding

The 13 `ENTRY_TP_SAME_BAR_ORDER_UNRESOLVED` cases are not merely SL-vs-TP ambiguity.

They contain a prior unresolved question:

> Was the theoretical entry actually filled before price reached TP?

Therefore a deterministic rule such as "Entry then TP" or "TP then Entry" must not be invented from OHLC alone.

This is directly relevant to fill semantics, which remains source-unresolved.

## Mechanical outcome bounds

The 33 currently decisive outcomes contain:

- Wins: 12
- Losses: 21
- Resolved-only WR: 36.36%
- Net R: -9R

If, strictly as uncertainty bounds, all 19 ambiguous outcomes are assigned wins:

- Wins: 31
- Losses: 21
- WR: 59.62%
- Net R: +10R

If all 19 ambiguous outcomes are assigned losses:

- Wins: 12
- Losses: 40
- WR: 23.08%
- Net R: -28R

These are mechanical uncertainty bounds only. They are not trading results, rule recommendations, or evidence for selecting an outcome convention.

The separate DATA_GAP outcome remains quarantined and is not assigned W/L in these bounds.

## Interpretation boundary

The current two-week replay cannot be treated as a clean statistical validation sample while a material portion of outcomes depends on unresolved intrabar/fill semantics.

The ambiguity is especially concentrated in SELL signals:

- SELL ambiguous: 14/27 = 51.85%
- BUY ambiguous: 5/26 = 19.23%

This asymmetry must not be interpreted as a directional edge or defect. It demonstrates that direction-level performance comparisons are currently confounded by unresolved outcome semantics.

## Source and canonical-status decision

No canonical geometry or execution rule is changed by this checkpoint.

Status:

- P-Gap semantic identity: unchanged
- Exact SP2L P-Gap candle roles/index: UNRESOLVED
- Fill semantics: UNRESOLVED
- Intrabar outcome ordering: UNRESOLVED
- Frozen Geometry: BLOCKED
- Production BUY/SELL generation: BLOCKED

Backtest performance is not used to resolve source ambiguity.

## Next admissible research step

Seek source evidence that explicitly binds entry/fill and intrabar execution semantics, or use a separately justified higher-resolution market-data forensic layer only as an empirical resolution aid. Neither route may silently become a canonical execution rule without source confirmation.

## Reproducibility

The raw forensic terminal output was generated from the replay artifact above using the temporary local script `.intrabar_forensic_tmp.py`. The temporary script was removed after execution and is intentionally not part of the repository.

This checkpoint is documentation-only and does not modify production or canonical Strategy A behavior.
