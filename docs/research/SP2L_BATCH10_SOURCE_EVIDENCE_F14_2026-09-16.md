# SP2L Batch 10 — F14 AB=CD Source Evidence — 2026-09-16

## Scope

Focused source-resolution pass for **F14 (AB=CD anchor construction and tolerance)**. Goal: determine whether accessible source evidence uniquely defines A/B/C/D anchors and the equality/tolerance rule. No geometry is frozen from implementation convenience or backtest performance.

## Repository audit

A repository search for `AB=CD` and `AB CD` did not surface an existing source-evidence matrix or canonical A/B/C/D anchor definition. Existing Batch 6/F14 records already classify AB=CD as a source-confirmed concept with anchors/tolerance unresolved; this pass extends that audit with the currently accessible web evidence.

## Evidence reviewed

### 1. Primary-author / author-associated source

The accessible primary-author SP2L page establishes the high-level model components and the two-leg continuation concept, but it does **not** expose a deterministic A/B/C/D anchor algorithm or numeric AB=CD tolerance in indexed text. No primary-source text located in this pass uniquely specifies whether anchors are candle OHLC extremes, bodies, swing pivots, spike boundaries, or another construction.

### 2. Secondary TradingFinder material

TradingFinder repeatedly describes SP2L as combining the spike move with a **2-leg AB=CD** structure and states that the spike is treated as the initial AB wave and the subsequent continuation as CD. It also describes the initial wave / point A in the context of stop placement and says the projected CD wave can be used as a profit target. However, the accessible text does not provide a complete deterministic A/B/C/D mapping, nor a numerical equality tolerance for AB versus CD.

The MT4/MT5 descriptions additionally describe entry after retracement/breakout and identify the spike movement as wave AB, but they still do not specify the exact B, C, and D anchor selection algorithm or an explicit AB=CD tolerance.

### 3. Secondary forum mirror

A secondary forum mirror repeats the concept that the spike is the initial impulse/wave AB and that the projected continuation is wave CD. It likewise does not expose a deterministic A/B/C/D anchor construction or tolerance rule.

## Finding — F14

Status: **SOURCE-CONFIRMED CONCEPT / A-B-C-D ANCHORS UNRESOLVED / AB=CD TOLERANCE UNRESOLVED**.

The accessible evidence is sufficient to confirm that AB=CD / two-leg structure is part of the SP2L conceptual model and that the spike is associated with the initial AB move. It is **not** sufficient to canonically determine:

- exact A anchor;
- exact B anchor;
- exact C anchor;
- exact D anchor;
- whether anchors use wick, body, close/open, or structural swing values;
- whether D is a projected target or an observed completed point;
- whether AB=CD means exact equality, a ratio, a tolerance band, or another source-defined condition;
- any numeric tolerance or rounding rule.

Therefore no executable AB=CD geometry is frozen in this batch.

## Gate consequence

F14 remains **BLOCKED for Frozen Geometry**. The project must not introduce an A/B/C/D formula, tolerance, Fibonacci substitution, Entry=C assumption, or wick/body convention merely to make the model executable.

The correct next step is further source resolution, preferably from the original training material/transcript or an authoritative source artifact that explicitly teaches the anchor construction and equality condition.

## Non-negotiables preserved

- No invented A/B/C/D anchors.
- No invented AB=CD tolerance.
- No wick/body convention inferred from secondary implementation text.
- No backtest-based selection among competing geometries.
- No production BUY/SELL logic introduced.
- 125R observation remains untouched.
