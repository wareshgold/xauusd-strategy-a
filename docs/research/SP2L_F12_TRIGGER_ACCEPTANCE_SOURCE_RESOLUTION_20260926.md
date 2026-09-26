# SP2L F12 Trigger Acceptance Source Resolution

Date: 2026-09-26
Status: SOURCE-PARTIAL / EXECUTABLE TRIGGER UNRESOLVED

## Primary evidence

The primary author transcript establishes several trigger/entry constructions, but does not select one universal executable trigger classifier.

### 1. Correction onset / previous-low relation — SOURCE-CONFIRMED

At 38:18–38:38 the author describes a bullish spike as a sequence of higher lows. When the next candle begins correction, correction is described as moving below the first low. At that point an order can be placed manually or as a predefined Limit.

This establishes the structural concept of correction crossing the referenced prior low, but the transcript does not freeze the exact candle index or universal "first low" selection across all structures.

### 2. Pending Limit entry — SOURCE-CONFIRMED

At 38:38 the author explicitly permits a predefined Limit at the correction location. At 38:53–39:26 he demonstrates a Buy Limit within the early three-candle construction.

This means the trigger concept must not be represented canonically as a market order waiting for a later close unless new source evidence supports that interpretation.

### 3. 1/2/3-candle family — SOURCE-CONFIRMED AS VARIANT FAMILY

The source material and existing decision matrix support multiple structural variants involving one, two, or three candles. The author also discusses additional signal-bar and key-bar confirmations at 40:57–41:03.

These are source-supported variants, not evidence that every variant shares one executable OHLC trigger.

### 4. Signal-bar / key-bar confirmation — SOURCE-CONFIRMED AS OPTIONAL VARIANT

At 40:57–41:03 the author describes seeing a signal bar and a key bar inside the setup. This is additional confirmation vocabulary. It does not provide a deterministic universal entry-price equation or precedence rule.

### 5. Activation — SOURCE-CONFIRMED CONCEPTUALLY

At 41:18 the author describes the next candle activating the order, resulting in a Buy with SL. Exact intrabar fill semantics remain unresolved.

## What source does NOT freeze

The following remain unresolved:

- exact referenced "first low" / "previous candle low" selection;
- exact bullish trigger candle index;
- exact bearish mirror mapping;
- whether trigger is touch, cross, close-through, or another event;
- exact entry price anchor once triggered;
- precedence among 1-, 2-, and 3-candle variants;
- precedence between structural trigger and signal-bar/key-bar confirmation;
- intrabar fill/touch/penetration semantics;
- spread/broker handling;
- deterministic cancellation if invalidation occurs before fill.

## Research-only discrimination fixtures

F12-001: correction reaches referenced prior low but does not close beyond it.

F12-002: correction wicks through the referenced low but closes above it.

F12-003: correction closes below the referenced low without a deeper intrabar penetration.

F12-004: one-, two-, and three-candle correction structures representing the same conceptual setup.

F12-005: competing candidate "previous/first low" references.

F12-006: signal-bar and key-bar confirmation present versus absent.

F12-007: pending Limit touched versus penetrated intrabar.

F12-008: bearish structural mirror.

Fixtures are designed to expose unresolved semantics. They must not select a canonical trigger through backtest performance.

## Canonical boundary

SOURCE-CONFIRMED:

- correction is part of the transition from Spike toward Leg 2;
- bullish correction can be described as moving below the relevant prior/first low;
- predefined Pending Limit is source-demonstrated;
- 1/2/3-candle structural variants exist;
- signal-bar/key-bar confirmations exist as additional variants;
- pending order can subsequently activate.

UNRESOLVED:

- universal executable trigger formula;
- exact candle/low/high indexing;
- touch/cross/close semantics;
- exact entry price anchor;
- variant precedence;
- fill semantics;
- complete bearish mirror.

## Gate

F12 = SOURCE-PARTIAL / EXECUTABLE TRIGGER UNRESOLVED.

Frozen Geometry remains BLOCKED. Untouched Validation, Fresh Holdout, and Production remain locked/off.

No current close-based EntryTrigger implementation is promoted to canonical status, and no replacement trigger formula is introduced here.

## Reopen condition

Reopen F12 only if new primary author evidence explicitly binds the trigger to a deterministic candle/index, OHLC event, entry-price anchor, or precedence rule.