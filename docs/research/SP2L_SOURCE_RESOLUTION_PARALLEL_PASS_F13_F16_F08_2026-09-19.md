# SP2L Source Resolution Parallel Pass — F13 / F16 / F08 — 2026-09-19

## Purpose

Record the next source-first pass after F11/F10/F12 review. The pass checks 2X lifecycle, Round Level, and relevant swing selection using only archived source evidence.

## Results

### F13 — 2X

Source confirms:
- 2X is a distinct second-position concept.
- It is optional in at least one teaching context.
- Author-associated material describes the secondary entry at approximately 50% of the distance from the entry point to SL.
- Primary artifacts distinguish the 2X level from the initial Buy/Entry and SL references.

Still unresolved:
- universal mandatory/optional status;
- exact reference state when entry is pending/filled/refreshed;
- exact price construction and tick rounding;
- sizing;
- pending vs immediate/confirmation-dependent execution;
- behavior when initial entry does not fill or is refreshed;
- fill and broker semantics;
- interaction with TP1/TP2 and Round Level.

**F13 = PARTIAL / UNRESOLVED.**

### F16 — Round Level

Source confirms:
- Round Level is explicitly taught.
- Primary examples include 250, 500, and 1000 point annotations.

Still unresolved:
- whether these are examples or universal/selectable intervals;
- source meaning of “point”;
- rounding/level construction function;
- purpose in setup/entry/target/risk/context;
- symbol/timeframe/volatility dependence;
- mandatory vs optional status;
- interactions with other SP2L geometry.

No interval or rounding formula is promoted.

**F16 = PARTIAL / UNRESOLVED.**

### F08 — Relevant swing selection

Source confirms:
- local structural points are relevant;
- bullish correction references low structure;
- later trigger wording references previous-candle low/high.

Still unresolved:
- first-important vs latest swing;
- pivot window;
- wick/body/close semantics;
- candidate precedence;
- dynamic update;
- exact bearish mirror;
- interaction with P-Gap and Buy Limit;
- whether swing equals spike-origin candle.

No conventional pivot/fractal rule is introduced.

**F08 = PARTIAL / UNRESOLVED.**

## Cross-field conclusion

These passes strengthen the semantic source map but do not close any executable blocker.

Current critical dependency chain remains:

P-Gap validity → structural/correction interpretation → trigger → entry/SL lifecycle → AB=CD / 2X / Round Level.

Because P-Gap executable construction and several downstream geometry fields remain unresolved, these results do not justify a new backtest, parameter promotion, Fresh Holdout, or production activation.

## Gate status

- Source Resolution: PARTIAL
- Frozen Geometry: BLOCKED
- Historical Validation: LOCKED
- Robustness/Stability: RESEARCH EVIDENCE ONLY
- Fresh Holdout: WAITING
- Production: BLOCKED
- Live Trading: DISABLED

## Next action

Continue with source evidence acquisition only where a concrete closure artifact could exist. Do not reopen generic P-Gap/FVG searching. The next useful closure targets are an explicit worked source calculation or unambiguous labeled artifact for one of the remaining executable fields.

No canonical geometry was changed in this pass.
