# SP2L SL / Structural Invalidation Source-Resolution Decision — 2026-09-14

## Purpose

Close the current source-resolution pass for the Strategy A stop / structural-invalidation dimension without inventing executable OHLC geometry.

This is a research evidence artifact, not a canonical strategy specification. Source meaning outranks implementation convenience, backtest performance, or parameter optimization.

## Evidence hierarchy

- Tier 1: direct source statement / transcript.
- Tier 2: direct source visual / chart example.
- Tier 3: official related source.
- Tier 4: secondary implementation.

Only Tier 1/2 evidence can directly establish source meaning for canonical geometry.

## Resolved semantic distinction

The source evidence consistently separates:

`Entry` ≠ `structural invalidation` ≠ `risk-budget position sizing`

The source geometry record also preserves the visual ordering:

`SL / invalidation → Entry → Leg 2`

Therefore a stop/invalidation level must not be derived from a percentage risk budget, ATR distance, fixed pip distance, or an arbitrary offset from Entry.

## Source-supported stop / invalidation meaning

The official-source reconciliation record includes the claim that the SL is placed behind the candle from which the Spike originated. The original lesson evidence independently establishes a deeper structural invalidation area and shows the stop/invalidation remaining below the deeper/base structure while the pending Entry can sit at a more recent correction level.

This is sufficient to preserve the following research semantic:

> Structural invalidation is anchored to the source's Spike-origin / base structural area, not to the risk budget and not automatically to the executable Entry price.

## What the source does NOT discriminate

The available source material does not provide a sufficiently explicit, universal machine-level definition for:

1. exact candle index of the Spike-origin candle in every variant;
2. exact OHLC field used for the boundary (`open`, `close`, `high`, or `low` as applicable);
3. wick-versus-body treatment;
4. whether the executable stop is exactly on the structural boundary or includes a source-defined buffer;
5. spread / execution adjustment;
6. whether the same construction applies identically to bullish and bearish variants.

The phrase "behind the candle" is semantically useful but is not, by itself, a deterministic formula.

## Negative controls

The following must NOT be promoted to canonical geometry from this pass:

- `stop = Entry - N` / `Entry + N`;
- fixed pip stop;
- ATR-derived stop;
- risk-percentage-derived stop price;
- wick-only or body-only rule inferred solely from a screenshot;
- arbitrary one-tick / one-point buffer;
- generic swing-low / swing-high algorithm substituted for the source's Spike-origin construction;
- assumed universal bullish/bearish mirroring without direct evidence.

## Adjudication

**Result: `SOURCE-DISCRIMINATED` at semantic level; `SOURCE-DOES-NOT-DISCRIMINATE` at executable OHLC level.**

The source discriminates structural invalidation from Entry and from risk-budget sizing, and supports a Spike-origin / base-structural placement concept. It does not uniquely determine the candle-level OHLC anchor, wick/body semantics, buffer, or universal mirrored implementation.

## Canonical consequence

Do not freeze an executable `stop_price` formula yet.

The deterministic engine must continue to represent at least these concepts separately when Strategy A geometry is eventually frozen:

- `entry_price`
- `invalidation_anchor`
- `stop_price`
- `risk_fraction`
- `position_size`

Only the first three become executable Strategy A geometry after source resolution is complete and manually approved.

## Gate impact

| Gate | Status |
|---|---|
| SOURCE RESOLUTION | **PARTIAL PASS — SL semantics narrowed** |
| SYNTHETIC FIXTURES | **REQUIRED for exact OHLC discrimination** |
| FROZEN GEOMETRY | **BLOCKED** |
| DEV | **LOCKED for Strategy A geometry** |
| UNTOUCHED VALIDATION | **LOCKED** |
| ROBUSTNESS / STABILITY | **LOCKED** |
| FRESH HOLDOUT | **LOCKED** |
| PRODUCTION | **LOCKED** |

## Required next fixture

Create an explicit source-discrimination fixture for the Spike-origin stop boundary with competing candidates:

- wick/base structural boundary;
- body boundary;
- generic opposite swing;
- risk-distance stop;
- optional source-defined buffer only if later evidence explicitly supports one.

The fixture result must remain `SOURCE-DOES-NOT-DISCRIMINATE` if source evidence cannot uniquely select one executable anchor.

## Governance boundary

No engine implementation, optimization, historical tie-breaking, validation promotion, or canonicalization is authorized by this document. Manual canonical approval by Ali remains mandatory.
