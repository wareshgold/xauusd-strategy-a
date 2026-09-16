# SP2L Batch 11 — F12 Trigger Source Evidence — 2026-09-16

## Scope

Focused source-resolution pass for **F12 (trigger taxonomy / 1-2-3 candle trigger family)**. Goal: determine whether accessible source evidence uniquely defines the trigger candle count and activation semantics. No trigger formula is frozen from secondary implementation behavior.

## Repository audit

A repository search for `trigger` did not surface an existing canonical trigger definition in the accessible code index. Existing synthetic fixture F12 intentionally preserves competing 1/2/3-candle trigger interpretations.

## Evidence reviewed

### 1. Primary-author source

The official/author-associated SP2L training index explicitly lists **«تریگر گیری از SP2L در استراتژی های شخصی»** (taking triggers from SP2L for personal strategies) as a training topic. The same index lists the SP2L definition, four spike types, P-Gap, 2L + Spike, order placement, 2X, levels/context, and examples. However, the indexed text does not expose a deterministic 1-candle, 2-candle, or 3-candle trigger taxonomy, nor a precise trigger activation rule.

The author's SP2L strategy page describes the model at a higher level: after the spike, the market corrects; once the Second Leg is triggered, entry is taken in the spike direction. It specifies the directional corrective condition (uptrend: corrective candle reaches previous candle low; downtrend: corrective candle reaches previous candle high), but it does not define a 1/2/3-candle trigger family or a canonical candle-count rule.

### 2. Secondary implementation evidence

TradingFinder material describes entry activation around spike/level retest and, in another implementation-oriented description, says entry can be activated by a breakout of the selected spike candle. These descriptions are secondary and do not establish a source-canonical trigger taxonomy. They also do not provide evidence sufficient to select one of the synthetic 1/2/3-candle interpretations.

### Finding — F12

Status: **SOURCE-CONFIRMED TRIGGER CONCEPT / 1-2-3 CANDLE TAXONOMY UNRESOLVED**.

The accessible source evidence confirms that triggering/entry activation is an explicit part of SP2L and is taught as a distinct concept. It does **not** uniquely determine:

- whether the canonical trigger is exactly one candle;
- whether a two-candle confirmation is required;
- whether a three-candle family is valid;
- whether the trigger is a close, break, retest, or another event;
- whether trigger semantics differ by bullish/bearish direction;
- whether the trigger is a source-level SP2L rule or a mechanism intended for adapting SP2L into another personal strategy.

Therefore F12 remains unresolved for executable frozen geometry.

## Gate consequence

F12 remains **BLOCKED for Frozen Geometry**. The project must not select a 1/2/3-candle interpretation by backtest performance, implementation convenience, or secondary indicator behavior.

## Non-negotiables preserved

- No invented trigger candle count.
- No invented close/break/retest semantics.
- No direction-specific trigger rule inferred without source confirmation.
- No profitability-based selection.
- No production BUY/SELL logic introduced.
- 125R observation remains untouched.
