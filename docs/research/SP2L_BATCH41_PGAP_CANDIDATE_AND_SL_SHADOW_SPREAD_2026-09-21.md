# SP2L P-Gap Candidate + Source-Confirmed SL Update — 2026-09-21

## Scope

This checkpoint records two different evidence classes.

1. **P-Gap executable detector:** research hypothesis only. The primary source
   confirms the Pressure Gap concept but does not provide a complete formula.
   AI may propose a candidate for engineering/research, but it is NOT
   canonical and cannot promote Frozen Geometry.
2. **Protective SL:** newly supplied direct teacher clarification from the
   operator. This is treated as source evidence pending archival provenance.

## P-Gap — research candidate, not canonical

Source-confirmed concept:

- P-Gap = Pressure Gap.
- Developmental context: trend pressure → pause/compression → trend-bar →
  continuation expectation.
- It is not established by the source as a generic three-candle imbalance.

### Candidate detector V1

For a bullish setup, define a pressure zone from the preceding pressure
sequence, followed by a pause/compression sequence and a bullish trend-bar.
For a bearish setup, use the directional mirror.

The detector must therefore be state-based rather than pretending that a single
3-candle OHLC inequality is the source definition.

Research state machine:

`PRESSURE_WINDOW -> PAUSE/COMPRESSION -> TREND_BAR -> P_GAP_CANDIDATE`

Candidate parameters are intentionally configurable and research-only:

- pressure-window length: configurable within the source-described 10–30 range;
- pause/compression length: configurable research parameter;
- trend-bar definition: configurable research parameter;
- directional mirror: explicit engineering symmetry, NOT source-confirmed.

No single parameter set is canonical.

### Important boundary

The existing `PGAPResearch.ts` three-candle imbalance observation remains
non-canonical and should not be relabeled as the P-Gap detector.

The V1 state-machine proposal is also non-canonical until independently
validated against additional primary evidence and synthetic fixtures.

## SL — newly supplied teacher clarification

Operator reports that the teacher explicitly answered:

> SL should be below the SPIKE SHADOW plus spread.

For bullish setups this maps to the lower shadow/wick of the spike candle,
with the protective stop placed below that shadow by the applicable spread
amount.

For bearish setups the directional mirror is the upper shadow/wick of the
spike candle, with the protective stop placed above that shadow by the
applicable spread amount.

### Canonical interpretation status

The following are source-confirmed from the reported teacher clarification:

- SL owner: **Spike candle**.
- Price field: **Spike shadow/wick extreme**.
- Protective placement: **beyond the shadow**.
- Spread must be included in the placement.

Still requiring explicit executable specification:

- exact arithmetic sign/direction;
- whether “spread” means current spread, entry-time spread, or another
  source-defined spread value;
- rounding/tick-size behavior;
- whether a fixed safety buffer exists in addition to spread;
- exact broker-side trigger semantics (bid/ask) for invalidation.

Until the teacher clarification is archived with provenance, the status is
**SOURCE-REPORTED / PENDING ARCHIVAL VERIFICATION**, not frozen geometry.

## Gate impact

- P-Gap concept: SOURCE-CONFIRMED.
- P-Gap executable geometry: RESEARCH CANDIDATE ONLY.
- SL concept/anchor: materially resolved by direct teacher clarification,
  pending archival provenance.
- Frozen Geometry: remains BLOCKED.
- No production BUY/SELL logic is changed.
- No existing backtest result is used to choose P-Gap parameters.

## Next engineering step

Build synthetic fixtures for the P-Gap state machine and SL shadow+spread
semantics, without promoting either the P-Gap parameterization or unresolved
execution semantics to production.
