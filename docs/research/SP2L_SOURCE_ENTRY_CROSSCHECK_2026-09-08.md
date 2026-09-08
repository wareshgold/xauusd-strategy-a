# SP2L Source Entry Cross-Check — 2026-09-08

## Question

Does the primary source video show that the SP2L pending-limit entry is contingent on a later breakout/reclaim of the last Spike candle, or is the order placed during correction before such a reclaim?

## Primary-source observations

The source video around 38:38 explicitly describes the next candle beginning correction as the price moving below the first Low in the bullish case, and says the order can be placed manually or as a pre-set limit at that point. Around 39:11 it says there is no need to wait for the next candle and the order can be placed within the initial three-candle sequence. Around 39:26 the Buy Limit is already placed and the stop distance is known before activation.

The visual sequence around the same section shows a horizontal Buy Limit level during the correction sequence, with SL below the early/origin structure. The diagram does not show a prerequisite last-Spike-candle reclaim before placing that pending order.

Later around 46:15–47:56, the source again describes the corrective trigger in terms of returning to the previous candle's Low for BUY / High for SELL and identifies that level as the important entry level for the second leg.

## Cross-check against secondary implementation

A secondary TradingFinder implementation describes a later breakout of the last Spike candle as an entry condition. That is a materially different event sequence from the source-video pending-limit semantics.

## Decision

**The primary source does not support promoting Last-Spike-Candle Breakout to the canonical entry rule.**

The source evidence is stronger for:

`SPIKE → CORRECTION → pending limit at source-defined previous/relevant Low/High`

than for:

`SPIKE → CORRECTION → wait for last-Spike-candle breakout/reclaim → entry`

The latter remains a secondary implementation hypothesis only.

## Remaining entry uncertainty

This cross-check does **not** resolve the exact executable price formula or exact candle index for the "previous/relevant Low/High" across all Spike variants. Those remain unresolved geometry items.

It also does not prove that every historical implementation labeled SP2L used identical order-management semantics.

## Gate impact

- Last-Spike-Candle Breakout as canonical entry: **REJECTED AS SOURCE RULE**
- Pending-limit during correction: **SOURCE-CONFIRMED SEMANTIC**
- Exact entry price formula: **UNRESOLVED**
- Exact relevant candle index across variants: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- Production: **UNCHANGED**

## Source hierarchy rule

Where the secondary implementation conflicts with the primary source video, the primary source controls. Profitability must not be used to reinterpret the source.
