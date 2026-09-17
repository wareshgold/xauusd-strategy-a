# SP2L Historical Session Source Search — Update 2026-09-17

## Scope
Resolve historical trading-session applicability for `OtetGroup-MT5 / XAUUSD.ecn`, with July 2026 as the first blocked month.

## Primary-source finding
The official Otet Markets July 2026 holiday page is discoverable at `https://otetmarkets.com/july-2026/`, but the live page currently redirects to the September 2026 calendar. Search indexing preserves one July-specific table entry:

- XAUUSD: **3 July 2026 — Close at 20:00**
- XAUUSD: **1 July 2026 — Normal Hours**

The source also states that displayed schedule times are **MT5 server time**. The current live financial-holidays page states that the market calendar is updated monthly.

## What this establishes
1. Otet had a July 2026 holiday schedule that explicitly included XAUUSD.
2. The July schedule contained a 3 July XAUUSD early-close exception at 20:00 MT5 server time.
3. Schedule times in Otet's calendar are server-time values, not UTC values.

## What this does NOT establish
This evidence does **not** establish the complete regular Monday-Friday session boundaries for `OtetGroup-MT5 / XAUUSD.ecn` during July 2026, nor does it prove that the current native-MQL5 session calendar remained unchanged throughout July.

It therefore cannot be used to convert the July M1 dataset into an `AUDITED_PASS` calendar artifact by inference.

## July data interaction
The July current-calendar audit remains:
- `AUDITED_FAIL`
- 257 missing expected timestamps
- 14 invalid timestamp jumps
- historical calendar applicability `UNRESOLVED`

No missing candles are fabricated, shifted, interpolated, or silently deleted.

## Decision
**Historical session resolution remains UNRESOLVED.**

The July holiday exception is useful evidence, but it is insufficient to canonicalize the complete historical session calendar for the exact MT5 server/symbol.

## Next evidence gate
Preferred next evidence remains, in order:
1. broker/terminal historical trading-hours specification for the exact symbol/server;
2. archived broker schedule or terminal report covering July 2026;
3. broker historical holiday calendar plus independently established server-time/UTC mapping sufficient to reconstruct exceptions without guessing;
4. otherwise preserve `UNRESOLVED`.

No SP2L geometry, P-Gap, AB=CD/F14, fill, execution, or lifecycle rule is changed by this research.
