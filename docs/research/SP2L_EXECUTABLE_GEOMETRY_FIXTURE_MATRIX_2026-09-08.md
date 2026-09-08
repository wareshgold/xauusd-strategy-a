# SP2L Executable Geometry Fixture Matrix — 2026-09-08

## Purpose

This document records the research-only synthetic stage after the semantic contract and component-level geometry fixtures. It tests whether combining source-confirmed components can uniquely recover executable geometry.

## Source boundary

The source confirms the following semantics:

- valid Spike requires P-Gap;
- Spike follows range/breakout/follow-through context;
- correction is described using the previous/relevant Low for bullish setups and previous/relevant High for bearish setups;
- the order may be prepared as a pending limit during correction;
- invalidation/SL is tied to the candle where the Spike originated;
- Leg 2 follows Leg 1 and the source describes AB=CD/equal-leg behavior;
- base TP is 1:1.

The source does **not** uniquely expose executable formulas for P-Gap boundaries/timing, exact entry candle/price, wick/body SL convention, Leg-1 anchors, or AB=CD tolerance.

## Cross-component fixtures

| Fixture | Scope | Expected gate |
|---|---|---|
| XC-BULL-PGAP-ENTRY-SL-LEG1 | full bullish chain | BLOCKED |
| XC-BEAR-PGAP-ENTRY-SL-LEG1 | full bearish chain | BLOCKED |
| XC-ENTRY-SEMANTIC-NOT-PRICE | pending-limit semantic vs actual fill | BLOCKED |
| XC-ABCD-NO-CLASSICAL-FIB | candle-level AB=CD vs classical Fibonacci mapping | BLOCKED |

## Interpretation rules

1. Cross-component consistency may eliminate an interpretation only when the source itself supplies the discriminating evidence.
2. A geometrically convenient result is not source evidence.
3. A profitable historical result is not source evidence.
4. Generic FVG/P-Gap equivalence remains rejected as canonical.
5. Market close-reclaim remains rejected as a substitute for the source's pending-limit semantics.
6. Classical harmonic A/B/C/Fibonacci mapping remains rejected as canonical.
7. A 50% retracement remains a secondary-management hypothesis, not the base entry.
8. No tolerance is introduced for AB=CD until source evidence defines it.

## Gate result

**FROZEN GEOMETRY: BLOCKED**

The combined fixtures demonstrate that semantic compatibility does not by itself resolve the missing executable anchors. Therefore the next research action must remain source-resolution work, not historical optimization.

## Production impact

None. These fixtures are research-only and are not imported by production Strategy A code. DEV, untouched VAL, robustness, fresh holdout, and production promotion remain locked.
