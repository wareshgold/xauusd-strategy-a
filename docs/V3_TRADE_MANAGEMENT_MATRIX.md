# V3 Trade-Management Experiment Matrix

This research-only extension compares exit-management hypotheses over the exact same frozen V3 entry population and M1 artifact. Entry detection, entry price, initial SL, volume, and source hashes remain unchanged.

## Supported first-stage modes

- `FIXED_RR`: fixed target at the supplied R multiple.
- `NO_TARGET`: initial stop only; unresolved if neither stop nor other exit occurs before data ends.
- `BREAK_EVEN`: move the stop to entry plus an optional non-negative R offset after a favorable excursion threshold.
- `TRAILING_R`: activate an R-distance trailing stop after a favorable excursion threshold; an optional fixed-R target can remain active.
- `BREAK_EVEN_TRAILING`: break-even protection followed by R-distance trailing; fixed-R target remains active.
- `TIME_EXIT`: close at the completed M1 bar close after a specified number of bars; an optional fixed-R target can remain active.

All stop changes calculated from a completed M1 bar apply only to the next bar. Same-bar stop/target hits and M1 gaps while open remain ambiguous. These are OHLC proxy mechanics, not tick-level broker fills.

## Explicit exclusions

Partial exits, scale-outs, ATR trailing, spread-aware bid/ask fills, slippage, commission, swap, and broker execution rules are not implemented by this first stage. They require explicit volume-allocation, source-data, and fill semantics. The existing point-based V3 trailing replay remains available and unchanged.

Every variant remains research-only, non-canonical, and NOT_VALIDATED. Parameter sweeps are exploratory and must not be treated as untouched validation or a production recommendation.
