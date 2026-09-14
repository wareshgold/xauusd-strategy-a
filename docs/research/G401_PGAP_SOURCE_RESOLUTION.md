# G401 — P-Gap Source Resolution

## Purpose

G401 is a source-resolution gate for the unresolved P-Gap geometry blocker carried by G400. It does not freeze executable P-Gap geometry.

## Evidence boundary

The repository currently confirms the semantic relationship that a valid breakout is associated with P-Gap, but the executable OHLC construction remains unresolved. Existing research explicitly distinguishes generic gaps, taxonomy candidates, timing variants, wick/body endpoints, size thresholds, tolerance, context, and anchors without promoting any of them to canonical geometry.

## Research hypotheses

G401 records four competing interpretations only as labels:

- generic three-candle range separation;
- body-boundary separation;
- wick-boundary separation;
- a source-specific P-Gap construction distinct from generic gap taxonomy.

All are non-canonical.

## Minimal-pair plan

Five minimal-pair families isolate:

1. wick versus body boundary;
2. generic gap versus breakout/follow-through context;
3. gap magnitude;
4. temporal ordering;
5. contextual placement inside a range versus at a source-described breakout.

The intended purpose is discrimination: identify which source-observable difference changes classification. It is not parameter optimization.

## Freeze policy

G401 remains `UNRESOLVED` until authoritative source material resolves the executable geometry. In particular, this gate does not invent:

- a P-Gap formula;
- an OHLC field selection;
- a minimum gap size;
- an overlap tolerance;
- an event-ordering rule;
- a contextual filter.

Synthetic fixtures can expose consequences of competing interpretations but cannot create source evidence.

## Promotion criterion

Only explicit authoritative source wording, source visual evidence, or a directly traceable source artifact that resolves the geometry may change the status. A backtest result, implementation convenience, or common trading convention is insufficient.

## Gate state

**UNRESOLVED / RESEARCH-ONLY**

G401 therefore does not clear the G400 P-Gap blocker and does not authorize executable Strategy A geometry, historical optimization, or production signals.
