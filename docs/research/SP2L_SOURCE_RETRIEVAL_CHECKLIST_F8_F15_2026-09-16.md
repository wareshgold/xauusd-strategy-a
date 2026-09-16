# SP2L Source Retrieval Checklist — F8–F15 — 2026-09-16

## Purpose

Define the exact source evidence required to close the remaining F8–F15 blockers. This checklist is a retrieval specification, not a canonical geometry definition. Historical profitability must not be used to choose among unresolved interpretations.

## Retrieval priority

### P0 — executable entry/invalidity geometry

#### F8 — Relevant swing selection
Need source evidence that uniquely answers:
- What makes a Low/High the relevant or important level?
- Is the first qualifying swing retained, or can the level evolve to a newer swing?
- What happens when multiple HL/LH candidates exist before entry?
- Is the reference a candle extreme, body boundary, close/open, or structural pivot?

Acceptable closure evidence:
- original training transcript with explicit rule;
- author teaching frame with labelled sequence and unambiguous level selection;
- author-controlled example whose candle sequence uniquely determines the selected level.

Do not close from:
- indicator implementation alone;
- visual preference;
- backtest performance.

#### F10 — Stop-loss / invalidation price semantics
Need source evidence that uniquely answers:
- Which exact price is meant by "behind the candle from which the Spike originated"?
- Wick high/low, body edge, open/close, or another structural boundary?
- Is a buffer used? If yes, what defines it?
- When is invalidation evaluated?

Do not infer a buffer or boundary from the existing backtest engine.

### P1 — order lifecycle and trigger

#### F11 — Pending-order lifecycle
Need source evidence that answers:
- Is an unfilled order retained when a newer level appears?
- When is it cancelled, replaced, refreshed, or superseded?
- Does a newer HL/LH automatically replace an older level?
- Is there an expiry measured in candles/time?
- What happens when the setup is structurally invalidated?

If the source is qualitative only, final status must remain `UNRESOLVED`; no state machine is invented.

#### F12 — Trigger taxonomy
Need explicit evidence for:
- one-candle vs two-candle vs three-candle trigger;
- exact trigger event: close, break, retest, touch, or other;
- whether trigger requires confirmation;
- whether semantics differ bullish vs bearish;
- whether the trigger is intrinsic SP2L or an adaptation mechanism for a personal strategy.

One isolated example is insufficient if it does not discriminate the complete rule.

### P2 — projection / secondary position

#### F14 — AB=CD geometry
Need explicit labelled evidence for:
- A anchor;
- B anchor;
- C anchor;
- D anchor;
- whether each uses wick/body/open/close/structural swing;
- whether D is projected or observed;
- whether AB=CD means exact equality, ratio, or tolerance band;
- numeric tolerance and rounding, if any.

No Fibonacci ratio or tolerance may be substituted without source confirmation.

#### F13 — 2X
Need explicit source evidence for:
- exact second-entry/2X price calculation;
- whether 50% Entry-to-SL is actually canonical;
- conditions for enabling 2X;
- whether 2X is pending or market execution;
- fill/re-entry semantics;
- relation to TP1/SL and whether both positions share the same invalidation.

Secondary 50% evidence remains a hypothesis only until primary confirmation.

### P3 — directional symmetry

#### F15 — Bearish mirror
Need at least one explicit bearish worked example sufficient to confirm:
- which bullish elements invert;
- whether entry/trigger semantics invert exactly;
- whether SL uses the mirrored Spike-origin reference;
- whether any part of the geometry is direction-specific rather than mathematically mirrored.

Current source evidence supports directional mirroring conceptually, but this checklist intentionally seeks explicit bearish examples before promoting universal symmetry.

## Retrieval targets

1. Original SP2L training video and transcript, especially lessons covering:
   - trigger taking;
   - 2X;
   - order placement;
   - 2L + Spike;
   - levels/context;
   - examples.
2. Author-controlled written material by Mohammad Ali Poursamadi.
3. Author-associated Telegram posts that link or describe the original training material.
4. Secondary TradingFinder material only for corroboration or candidate terminology; never as sole canonical authority when primary evidence is available.

## Search terms — English

`SP2L trigger`, `SP2L entry level`, `SP2L second leg`, `SP2L stop loss`, `SP2L 2X`, `SP2L AB=CD`, `SP2L bearish example`, `SP2L order placement`, `SP2L retest`, `SP2L HL LH`.

## Search terms — Persian

`SP2L تریگر`, `تریگر گیری از SP2L`, `تریگر اسپایک`, `کندل تریگر`, `نحوه ورود`, `نحوه و دلیل ورود در 2x`, `اسپایک دو لگ`, `لگ دوم`, `سطح ورود`, `حد ضرر`, `کندل مبدا اسپایک`, `AB=CD`, `موج AB`, `موج CD`, `های بالاتر`, `لوهای بالاتر`, `لوئر های`, `لوئر لو`.

## Evidence recording protocol

For every candidate source artifact record:
- source URL or repository reference;
- source authority class: primary / author-associated / secondary;
- exact date/version when available;
- relevant timestamp/page/frame;
- verbatim short excerpt or precise visual description;
- rule question answered;
- competing interpretations eliminated;
- remaining ambiguity;
- closure status: `SOURCE-CLOSED`, `PARTIALLY CLOSED`, or `UNRESOLVED`.

## Closure rule

A fixture can become source-closed only when the evidence uniquely determines the rule required for deterministic implementation. If two or more materially different interpretations remain compatible with the evidence, retain `UNRESOLVED`.

## Current gate

F8–F15 are not fully source-closed. Frozen Geometry remains **BLOCKED**. Untouched Validation, Robustness/Stability, Fresh Holdout, and Production remain locked/off.

The baseline implementation and observed R-multiple behaviour are forensic artifacts only and cannot be used to close these source questions.

125R remains untouched.
