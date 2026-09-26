# F10 — Stop Anchor / Invalidation Geometry Source Discrimination

Date: 2026-09-26
Status: SOURCE-PARTIAL / EXECUTABLE GEOMETRY UNRESOLVED

## Purpose

Resolve the Strategy A structural invalidation / stop-loss geometry without allowing backtest performance, risk-budget constraints, or implementation convenience to define the rule.

## Source-confirmed ceiling

The primary SP2L transcript establishes that the pending Buy Limit has a separate stop distance and that if price returns to the structural invalidation area, the scenario is no longer valid. The source therefore distinguishes entry from invalidation and treats the stop as a consequence of the trade hypothesis becoming invalid.

The existing research audit additionally records that the demonstrated bullish construction places entry near a relevant/latest higher-low while structural invalidation is deeper, near the original/base structural low. This contradicts treating the correction extreme itself as the canonical structural stop reference.

The source does **not** currently establish:

- exact candle index for the stop anchor;
- wick vs body semantics;
- open vs close semantics;
- whether the anchor is a candle extreme or a structural swing extreme;
- fixed or dynamic stop buffer;
- spread/broker execution offset;
- numeric risk-distance threshold as part of geometry.

Therefore none of those fields is frozen.

## Current implementation boundary

`src/domain/strategy-a/StructureStopLoss.ts` currently calculates:

- BUY: `correction.extremePrice - buffer`
- SELL: `correction.extremePrice + buffer`

This remains research implementation only. It must not be promoted to canonical geometry.

## Synthetic discrimination fixtures

These fixtures are deliberately constructed so that competing stop interpretations produce different answers.

| Fixture | Discriminator | Expected source question | Canonical status |
|---|---|---|---|
| F10-001 | correction extreme vs deeper base structural low | Is invalidation tied to the correction or the original/base structure? | unresolved until source discriminates |
| F10-002 | wick extends beyond body at candidate stop candle | Wick or body boundary? | unresolved |
| F10-003 | open/close differ from wick extreme | Which OHLC field defines invalidation? | unresolved |
| F10-004 | same structural swing formed by multiple candles | Candle-specific or structural-turn anchor? | unresolved |
| F10-005 | entry level differs materially from invalidation level | Are Entry and SL independently anchored? | source supports separation; exact anchors unresolved |
| F10-006 | same structural geometry with different nominal risk budgets | Does risk budget move the stop? | source says structural invalidation is distinct from risk budget |
| F10-007 | bearish mirror of F10-001..006 | Is the same construction independently established for SELL? | source-consistent, not independently frozen |
| F10-008 | zero vs non-zero buffer around same anchor | Is any fixed buffer source-defined? | unresolved |

## Fixture gate

A fixture may only promote a stop rule when primary source evidence explicitly discriminates the competing interpretations. A backtest cannot resolve any F10 ambiguity.

Passing the fixture suite therefore means **the ambiguity was represented correctly**, not that one candidate was selected.

## Non-rules

Do not promote any of the following from this checkpoint:

- correction extreme as canonical SL;
- original/base candle low/high as a universal formula;
- wick-based stop;
- body-based stop;
- open/close stop;
- fixed pip/point buffer;
- spread buffer;
- maximum-risk filter as stop geometry.

## Gate consequence

F10 remains PARTIAL / UNRESOLVED. Frozen Geometry remains BLOCKED. Untouched validation and production remain locked.

## Next source action

Only new primary author evidence showing the actual stop marker/anchor should be used to discriminate F10-001 through F10-008. If no such evidence is found, F10 reaches source ceiling and remains explicitly unresolved.
