# SP2L P-Gap / Breakout / Spike Relationship Gate — 2026-09-22

## Objective
Resolve the source relationship between Spike, Breakout/Valid BO, and P-Gap without promoting an executable P-Gap formula.

## Source evidence re-audited
- SP2L is Spike → 2 Leg.
- The source labels a valid breakout as associated with P-Gap.
- P-Gap is explicitly distinguished from common/E-Gap.
- The demonstrated bullish sequence contains directional Spike structure, breakout/follow-through, correction, and a pending Limit.
- The source records do not uniquely identify the P-Gap candle indices or OHLC boundaries.
- The existing three-candle imbalance detector is explicitly research-only and cannot be promoted from performance or implementation behavior.

## Relationship findings

### 1. Spike → Breakout
**SOURCE-SUPPORTED SEMANTIC RELATIONSHIP.**
The source teaching places the breakout/follow-through after the directional Spike construction. The exact candle-level breakout classifier remains unresolved.

### 2. Breakout → P-Gap
**SOURCE-CONFIRMED SEMANTIC PREREQUISITE.**
The source explicitly associates a valid breakout with P-Gap. This is stronger than merely observing that P-Gap can occur near a breakout.
However, the source evidence available in the repository does not uniquely specify:
- which candle creates the P-Gap;
- which candle(s) form its boundaries;
- whether the Spike candle is itself one of those boundaries;
- whether the breakout candle is one of those boundaries;
- whether equality is permitted;
- the exact OHLC field used at each boundary.

### 3. P-Gap → 2-Leg sequence
**SOURCE-SUPPORTED SEMANTIC SEQUENCE.**
The source-aligned worked examples support the broader sequence:

Spike construction → valid breakout/P-Gap → correction/pending Limit → second leg

This does not authorize treating every detected three-candle imbalance as a valid P-Gap.

### 4. Directional symmetry
**UNRESOLVED.**
A synthetic bearish mirror is deterministic engineering, but the current archived source records do not provide sufficient frame-level discrimination to promote it as universal canonical geometry.

## Rejected implementation shortcuts
- `right.low > left.high` / `right.high < left.low` as canonical P-Gap;
- fixed candle indices;
- `+1` tick/pip thresholds;
- equality assumptions;
- using backtest performance to select the P-Gap geometry;
- defining breakout solely as a generic high/low break;
- assuming Spike candle = P-Gap candle;
- assuming Breakout candle = P-Gap boundary;
- assuming a universal three-candle construction.

## Source-resolution consequence
The relationship is now narrowed to:

Spike construction → source-recognized Breakout/Valid BO → P-Gap prerequisite → correction/Limit → 2-Leg

The semantic chain is source-supported, but the executable P-Gap/Breakout geometry remains unresolved.

## Next discriminating evidence
The minimum useful artifact is a source frame/worked example where the same example visibly identifies:
1. Spike candle(s);
2. breakout/reference candle;
3. both P-Gap boundaries;
4. correction/entry reference.

If those are not available at auditable resolution, the ambiguity remains open.

## Gate status
- Spike → Breakout relationship: **SOURCE-SUPPORTED**
- Valid BO ↔ P-Gap relationship: **SOURCE-CONFIRMED SEMANTICALLY**
- Executable P-Gap geometry: **UNRESOLVED**
- Executable breakout classifier: **UNRESOLVED**
- Bearish universal mirror: **UNRESOLVED**
- Frozen Geometry: **BLOCKED**
- DEV/validation/holdout: **LOCKED**
- Production: **OFF**

No production or canonical strategy code was changed.