# SP2L Batch 13 — Source Evidence F11/F12 — 2026-09-16

## Scope

P1 source retrieval for:
- F11 — pending-order lifecycle / refresh / supersession
- F12 — trigger taxonomy and trigger event

Source meaning outranks implementation or backtest performance. This record does not promote secondary implementation behaviour to canonical Strategy A geometry.

## Sources reviewed

### 1. Author-associated Telegram post — primary/author-associated evidence

Source: Poursamadi Telegram channel/post reproducing the official SP2L training-video outline.

The post explicitly lists training sections for:
- `نحوه اوردگذاری با این استراتژی SP2L` — how to place orders with SP2L;
- `نحوه و دلیل ورود در 2x` — how/why to enter in 2X;
- `تریگر گیری از SP2L در استراتژی های شخصی` — taking triggers from SP2L in personal strategies;
- examples and detailed trade walkthroughs.

It also links the SP2L training video `7HEC5mO3d3U`.

Important boundary: the indexed Telegram post exposes the curriculum topics, not the deterministic order-lifecycle or trigger-timing rule itself. Therefore it identifies authoritative training material but does not close F11 or F12.

### 2. Video-summary transcription/index — secondary evidence

The indexed summary of the linked SP2L video reports:
- breakout validation involving a current candle closing above/below a level;
- the next candle not overlapping back into the prior range;
- a set-and-forget execution concept using predefined SL/TP/limit orders;
- limit-order handling is discussed in the context of knowing SL distance before activation.

The summary is not the original transcript, and its presenter attribution is not sufficiently explicit for canonical rule promotion. Subtitle/summary errors are also documented by the source. These observations therefore remain corroboration only.

### 3. TradingFinder secondary SP2L description

The protected TradingView description states that each HL/LH is a potential entry level and that actual entry occurs when price returns to retest that level. It describes bullish and bearish cases symmetrically.

This is useful corroboration for a retest-based entry concept, but it does not specify:
- whether the first or latest pending level survives;
- whether a newer HL/LH replaces an older pending order;
- cancellation or expiry conditions;
- one-, two-, or three-candle trigger taxonomy;
- whether activation is touch, intrabar break, close, or confirmed close.

The script is protected/closed-source, so implementation details cannot be audited as source truth.

## F11 — Pending-order lifecycle

### Finding

`UNRESOLVED`

### What is source-supported

The author-associated training outline confirms that order placement is explicitly taught in the source material. Secondary material also supports the existence of retest-based entry levels and limit-order concepts.

### What remains unresolved

No retrieved source uniquely determines:
- retain vs replace when a newer HL/LH appears;
- cancellation/supersession conditions;
- pending-order refresh rules;
- time/candle expiry;
- invalidation behaviour while an order is pending.

Therefore no pending-order state machine is introduced.

## F12 — Trigger taxonomy

### Finding

`SOURCE-CONFIRMED TRIGGER CONCEPT / EXACT TAXONOMY UNRESOLVED`

### What is source-supported

The author-associated training outline explicitly includes trigger-taking from SP2L in personal strategies. Secondary TradingFinder material describes entry activation when price returns to retest an HL/LH level.

The video-summary index additionally reports a breakout-validation example involving candle close and subsequent non-overlap, but this is secondary summary evidence and is not sufficient to establish the canonical SP2L trigger rule.

### What remains unresolved

No source retrieved here uniquely determines:
- one-candle vs two-candle vs three-candle trigger;
- touch vs intrabar break vs candle close;
- whether confirmation is mandatory;
- whether trigger semantics differ by bullish/bearish direction;
- whether the trigger-taking material is canonical SP2L execution or an adaptation mechanism for personal strategies.

## Canonical-rule decision

No new executable rule is promoted for F11 or F12.

In particular, the following are NOT canonicalized:
- automatic replacement by the newest HL/LH;
- pending-order expiry in N candles;
- first-level retention;
- touch-to-fill semantics;
- close-confirmation semantics;
- one/two/three-candle trigger family;
- breakout close + next-candle non-overlap as the SP2L canonical trigger.

## Gate consequence

- Source Resolution: PARTIAL PASS
- F11: BLOCKED / UNRESOLVED
- F12: BLOCKED / EXACT TAXONOMY UNRESOLVED
- Frozen Geometry: BLOCKED
- Untouched Validation: LOCKED
- Robustness/Stability: LOCKED
- Fresh Holdout: LOCKED
- Production: OFF
- 125R: UNTOUCHED

## Next evidence target

Return to the original training artifact itself and obtain timestamped transcript/frame evidence around:
1. order placement and what happens when another level appears;
2. trigger-taking examples and exact candle event;
3. at least one complete bullish and bearish worked example.

No backtest variant should be used to select among these unresolved interpretations.
