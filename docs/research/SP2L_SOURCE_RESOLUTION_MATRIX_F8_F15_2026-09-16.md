# SP2L Source Resolution Matrix — F8–F15 — 2026-09-16

## Purpose

Consolidate the current source-first status of synthetic fixtures **F8–F15** after Batches 8–11. This matrix records what accessible evidence supports and, critically, what remains unresolved. It is a gate artifact, not a geometry specification.

## Source-resolution matrix

| Fixture | Topic | Current source status | Canonical executable rule? | Freeze impact |
|---|---|---|---|---|
| F8 | First important swing / evolving swing selection | **CONCEPT PARTIALLY DISCRIMINATED / SELECTION ALGORITHM UNRESOLVED** | No | BLOCKED |
| F9 | Entry vs Leg-2 start | **SOURCE-CONFIRMED SEPARATION / ACTIVATION PARTIALLY RESOLVED** | No | BLOCKED |
| F10 | Structural invalidation vs SL | **SOURCE-CONFIRMED ORIGIN REFERENCE / PRICE SEMANTICS UNRESOLVED** | No | BLOCKED |
| F11 | Pending-order replacement / refresh | **UNRESOLVED** | No | BLOCKED |
| F12 | 1/2/3-candle trigger taxonomy | **SOURCE-CONFIRMED TRIGGER CONCEPT / TAXONOMY UNRESOLVED** | No | BLOCKED |
| F13 | 2X | **SOURCE-CONFIRMED CONCEPT / SECONDARY 50%-DISTANCE EVIDENCE / CANONICAL FORMULA UNRESOLVED** | No | BLOCKED |
| F14 | AB=CD anchors and tolerance | **SOURCE-CONFIRMED CONCEPT / A-B-C-D ANCHORS UNRESOLVED / TOLERANCE UNRESOLVED** | No | BLOCKED |
| F15 | Bearish mirror | **SOURCE-CONFIRMED DIRECTIONAL MIRROR / EXACT EXECUTION GEOMETRY UNRESOLVED** | No | BLOCKED |

## Evidence boundaries

### F8

Primary-author material supports the directional corrective condition (bullish correction reaches the previous candle low; bearish correction reaches the previous candle high), but does not uniquely define the deterministic selection of the first important swing versus an evolving/latest swing. Secondary HL/LH material is treated as supporting evidence only.

### F9

Primary-author material distinguishes the Second Leg trigger from the Entry Level and states that entry follows once the Second Leg is triggered. This supports separation of the concepts but does not define every candle-path activation case or an executable timestamp/price rule. `Entry = C` remains unconfirmed.

### F10

Primary-author material places SL behind the candle from which the Spike originated. The exact price boundary (wick/body/open/close), buffer, and invalidation timing remain unresolved.

### F11

No deterministic source rule has been located for retaining, cancelling, replacing, or refreshing an unfilled pending order after a newer level/setup appears. No replacement threshold or state machine is canonical.

### F12

Trigger-taking is explicitly a taught SP2L topic, and the strategy description refers to the Second Leg being triggered. Accessible source text does not discriminate exactly one, two, or three candles, nor close/break/retest activation. Secondary implementation descriptions are not sufficient for canonical selection.

### F13

2X is an explicit training topic. Secondary sources converge on a 50%-distance concept, but the accessible primary text does not expose enough detail to prove that exact formula, its conditions, or re-entry/fill semantics. Therefore `2X = 50% of Entry→SL` is not canonical.

### F14

AB=CD / two-leg structure is source-supported conceptually, including association of the Spike with the initial AB move. Exact A/B/C/D anchors, wick/body semantics, projected versus observed D, equality/ratio interpretation, and numeric tolerance remain unresolved.

### F15

Primary-author material explicitly describes both bullish and bearish directional conditions and states entry follows the Spike direction, while SL references the Spike-origin candle. This supports directional mirroring at concept level. It does not by itself prove every lower-level geometry/execution detail is a mathematical mirror.

## Gate decision

**Source Resolution: PARTIAL PASS** — several concepts and references are source-supported, but executable geometry is not fully resolved.

**Frozen Geometry: BLOCKED** — F8–F15 contain unresolved executable semantics that cannot be selected by backtest performance or implementation convenience.

**Untouched Validation: LOCKED** — no frozen canonical geometry exists yet.

**Robustness/Stability: LOCKED**.

**Fresh Holdout: LOCKED**.

**Production: OFF**.

## Explicit non-canonical items

The following must remain unresolved and must not be promoted merely to make the engine executable:

- swing-selection algorithm;
- exact Entry activation/timestamp/price semantics;
- exact SL price boundary and buffer;
- pending-order replacement/refresh threshold and lifecycle;
- 1/2/3-candle trigger family;
- exact 2X formula and fill semantics;
- A/B/C/D AB=CD anchors and tolerance;
- any assumption that bullish/bearish symmetry resolves the underlying lower-level geometry.

## Research discipline

This matrix does **not** authorize variant backtests to choose among unresolved interpretations. Backtesting begins only after source-confirmed rules are frozen. Synthetic fixtures remain useful for preventing accidental geometry invention and for proving deterministic handling once the source semantics are resolved.

The existing implementation/report R-multiple semantics and the observed 125R extreme remain separate forensic concerns and are not used to resolve any F8–F15 item.
