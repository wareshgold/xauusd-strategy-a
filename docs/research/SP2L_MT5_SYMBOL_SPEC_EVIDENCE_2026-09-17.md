# SP2L MT5 Symbol Specification Evidence — 2026-09-17

## Status

`OBSERVED_CURRENT_TERMINAL_EVIDENCE`

This artifact records a diagnostic output supplied from the Otet Group MT5 Terminal for `XAUUSD.ecn` on 2026-09-17. It is current terminal/symbol evidence only. It is **not** historical proof of the July/August/April-May-June 2026 specification.

## Provenance

- Terminal: `Otet Group MT5 Terminal`
- Company: `Otet Group Ltd.`
- Server: `OtetGroup-MT5`
- Terminal build: `6182`
- Symbol: `XAUUSD.ecn`
- Symbol custom: `0`
- Symbol selected: `1`
- Path: `Metals\\XAUUSD.ecn`
- Description: `Gold vs US-Dollar`
- Base currency: `USD`
- Profit currency: `USD`
- Margin currency: `USD`
- Diagnostic chart timeframe: `M5`
- Diagnostic tick time: `2026.09.17 12:18:40`

## Current symbol specification

| Property | Observed value |
|---|---:|
| trade_mode | 4 |
| trade_calc_mode | 4 |
| trade_execution | 2 |
| filling_mode | 3 |
| order_mode | 127 |
| expiration_mode | 15 |
| order_gtc_mode | 0 |
| digits | 2 |
| point | 0.0100000000 |
| tick_size | 0.0100000000 |
| tick_value | 1.0000000000 |
| tick_value_profit | 1.0000000000 |
| tick_value_loss | 1.0000000000 |
| contract_size | 100.0000000000 |
| volume_min | 0.0100000000 |
| volume_max | 100.0000000000 |
| volume_step | 0.0100000000 |
| volume_limit | 0.0000000000 |
| stops_level_points | 0 |
| freeze_level_points | 0 |
| spread_points | 18 |
| spread_float | 1 |
| terminal_trade_allowed | 1 |

## Current tick snapshot

- Bid: `4314.6800000000`
- Ask: `4314.8600000000`
- Last: `0.0000000000`
- Tick volume: `0.0000000000`

The tick snapshot is transient and is not a strategy rule or historical dataset.

## Interpretation boundaries

This evidence establishes the observed current symbol specification on the identified terminal/server. It does **not** establish:

- historical symbol specification for July 2026;
- historical session boundaries for July 2026;
- historical execution/fill semantics for the research dataset;
- canonical SP2L entry, P-Gap, spike, AB=CD/F14, stop, target, lifecycle, or fill rules;
- authorization for automated BUY/SELL production decisions.

The existing historical-session status therefore remains `UNRESOLVED` until historical applicability is independently evidenced.

## Research consequence

The next data-provenance gate remains historical session/calendar resolution and audited acquisition. Current symbol specification can inform future execution-engineering documentation, but must not be retroactively applied to historical data without evidence.

## Source

Diagnostic: `scripts/mt5_mql5_symbol_spec_metadata.mq5`

The diagnostic was compiled successfully with `0 errors, 0 warnings` and executed on the identified Otet terminal. The output was supplied directly from the terminal Experts log for this research session.
