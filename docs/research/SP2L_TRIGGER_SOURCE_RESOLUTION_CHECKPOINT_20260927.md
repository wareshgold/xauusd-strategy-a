# SP2L Trigger Source Resolution Checkpoint — 2026-09-27

## Primary-source review

The official author page was re-checked on 2026-09-27.

Official source:
https://poursamadi.com/en/sp2l-strategy-spike-2leg-by-mohammad-ali-poursamadi/

The source describes the Second Leg as follows:

- Uptrend: wait for the corrective candle to reach the low of the previous candle.
- Downtrend: wait for the corrective candle to reach the high of the previous candle.
- Once the Second Leg is triggered, enter in the direction of the spike.

The same page separately describes the structure as Spike → correction → Second Leg/Entry and says the SL is behind the candle from which the spike originated. It does not publish a machine-readable candle-index equation or an explicit intrabar execution rule. cite source-search-20260927-official-sp2l

## Evidence interpretation

The wording provides meaningful source evidence that:

1. The trigger is associated with the corrective/Second-Leg candle.
2. BUY uses a previous-candle Low reference.
3. SELL uses a previous-candle High reference.
4. The trigger is a price reaching a level, rather than an explicit close condition.

However, the wording does NOT uniquely resolve:

- Which exact candle is "previous candle" when represented as OHLC indices.
- Whether the correction candle is necessarily the immediately next candle after the spike.
- Whether "reach" means touch, penetration, or close beyond the level.
- Whether the entry price is the reached level, the correction candle extreme, or another execution price.
- Whether the second-leg trigger can occur after more than one correction candle.
- Exact order/fill semantics.

## Reconciliation relevance

The setup-level reconciliation on the 2026-09-14 through 2026-09-25 MT5 M1 window found:

- V2 setups: 139
- Source-aligned setups: 53
- Common: 53
- V2-only: 86
- Source-aligned-only: 0

Segment-aware forensic classification of all 86 V2-only cases:

- TRIGGER_TIMING_OR_ACCEPTANCE: 69
- TRIGGER_AND_TRIGGER_BODY_CONSTRAINT: 13
- SOURCE_RISK_CONSTRAINT: 4

This evidence localizes implementation divergence primarily to trigger semantics, but it does not establish which interpretation is source-canonical.

## Decision

Trigger geometry remains **SOURCE-UNRESOLVED**.

No canonical trigger rule is promoted from the reconciliation or backtest results.

## Next source-resolution method

Build synthetic fixtures that isolate one semantic at a time:

### Fixture T1 — immediate correction candle
The first post-spike correction candle reaches the previous candle Low/High.

### Fixture T2 — delayed reach
The first correction candle does not reach the previous candle Low/High; a later correction candle does.

### Fixture T3 — exact touch
The relevant Low/High equals the previous candle Low/High exactly.

### Fixture T4 — penetration
The relevant Low/High moves beyond the previous candle Low/High.

### Fixture T5 — close-only
The candle closes beyond the reference level but its extreme does not provide the same interpretation.

### Fixture T6 — multi-candle correction
Several correction candles occur before the reference level is reached.

The fixtures are diagnostic only. They must not be used to select a rule by backtest performance. A fixture becomes a canonical rule only when primary-source evidence resolves the corresponding semantic.

## Gate

Current stage remains:

SOURCE RESOLUTION → SYNTHETIC FIXTURES

Not yet:

FROZEN GEOMETRY / OPTIMIZATION / PRODUCTION
