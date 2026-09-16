# SP2L Batch 14 — Source Evidence F11/F12 — 2026-09-16

## Scope
P1 source retrieval for pending-order lifecycle (F11) and trigger taxonomy (F12). Source meaning outranks implementation or performance. No canonical geometry is introduced.

## Sources reviewed

1. Author-associated Telegram post linking the SP2L training video `https://youtu.be/7HEC5mO3d3U` and describing it as the SP2L strategy training sequence.
   - Authority: author-associated distribution / provenance evidence.
   - The post identifies the video as SP2L Strategy and points to the original YouTube artifact.
2. Search-indexed summary of the linked SP2L video at `https://youtubesummary.com/summary/7HEC5mO3d3U`.
   - Authority: secondary transcript/summary; not primary canonical text.
   - It reports a breakout-validation description: the current candle closes above/below a level and the next candle does not overlap back into the prior range. It also describes set-and-forget execution with SL/TP or limit orders placed upfront.
3. TradingFinder secondary SP2L description.
   - It states that in bullish conditions HLs are potential buy levels and in bearish conditions LHs are potential sell levels, with entry activated when price returns to retest the level.
   - This is secondary implementation/description evidence and is not sufficient alone to freeze exact trigger or order lifecycle semantics.

## F11 — Pending-order lifecycle

### Evidence
The reviewed sources establish that order placement / pending-order concepts exist in the SP2L teaching material, and the video summary describes placing trade controls upfront, including limit orders. However, none of the reviewed evidence uniquely specifies the lifecycle after a pending level is created.

Unresolved questions:
- whether an older unfilled level remains active after a newer HL/LH appears;
- whether a newer level replaces/supersedes the older order;
- cancellation/refresh rules;
- candle/time expiry;
- invalidation behaviour before fill;
- whether multiple pending levels may coexist.

### Status
`UNRESOLVED`

No state machine, expiry, replacement threshold, or cancellation rule is promoted to canonical geometry.

## F12 — Trigger taxonomy

### Evidence
The secondary video summary reports a breakout-validation sequence in which the current candle closes beyond a level and the following candle does not overlap back into the prior range. Separately, TradingFinder describes SP2L entry levels as HL/LH structures and says the actual entry activates when price returns to retest the level.

These sources provide useful discrimination of the broad concept:
- a trigger/activation event exists;
- retest of a structural level is part of the described SP2L entry process;
- a breakout-validation concept is discussed in the training-video summary.

They do NOT uniquely establish the canonical executable taxonomy requested by F12:
- one-candle vs two-candle vs three-candle trigger;
- touch vs break vs close as the sole activation event;
- intrabar vs bar-close semantics;
- whether confirmation is mandatory for every setup;
- whether the breakout-validation sequence is intrinsic SP2L geometry or a contextual explanation/variant.

### Status
`SOURCE-CONFIRMED TRIGGER CONCEPT / EXACT TAXONOMY UNRESOLVED`

No 1/2/3-candle rule, close-only rule, wick-touch rule, or confirmation rule is frozen.

## Gate consequence
F11 and F12 remain blockers for Frozen Geometry. P1 source retrieval produced evidence but not a deterministic executable closure.

No backtest variant was selected using profitability, win rate, expectancy, drawdown, or any other performance metric.

125R remains untouched.
