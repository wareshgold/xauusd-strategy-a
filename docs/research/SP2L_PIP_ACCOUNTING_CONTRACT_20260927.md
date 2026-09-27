# SP2L Pip Accounting Contract

Status: RESEARCH ONLY.

## Purpose

Make performance reporting comparable without pretending that every symbol has the same pip definition.

## Rules

1. Store MT5 point and digits for every symbol/run.
2. Store the derived pip_size in every artifact.
3. FX non-JPY pairs use 0.0001 price units per pip.
4. FX JPY pairs use 0.01 price units per pip.
5. XAUUSD reports raw price movement and a broker-point-equivalent pip metric; it must not be mixed with FX pip economics.
6. R remains the normalized risk metric.
7. Gross pips and transaction costs are reported separately.
8. Net transaction-cost calculations require explicit commission/spread inputs; no broker cost is invented when MT5/account data does not provide it.
9. Volume is stored per candidate/run so minimum-volume constraints cannot be silently ignored.
10. Pip reporting never changes setup detection, entry, SL, TP, or exit logic.

## Required per-trade fields

- symbol
- point
- digits
- pip_size
- volume_lots
- entry
- exit
- gross_pips
- gross_price_move
- realized_R
- commission
- spread assumption/source
- net_cost
- completed

## Statistical reporting

Aggregate by week first, then by symbol/year. Report both gross and cost-aware metrics whenever the cost inputs are authoritative.

No cross-symbol ranking is implied by pip totals because pip monetary value, contract size, volume, spread and commission differ.
