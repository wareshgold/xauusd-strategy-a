# SP2L F10 — Spike-Origin Stop Boundary Source-Discrimination Fixture

Date: 2026-09-14
Status: SOURCE-DOES-NOT-DISCRIMINATE at executable OHLC level
Canonical status: NOT CANONICAL

## Purpose

F10 isolates the remaining executable ambiguity in the already source-supported distinction between structural invalidation and risk-budget stop placement.

This is a synthetic source-discrimination fixture, not historical evidence, optimization data, or a production rule. Source meaning outranks any backtest result.

## Source-aligned invariant

The source evidence supports a structural invalidation concept associated with the Spike/base structure and distinguishes that invalidation from the executable Entry and from risk-budget position sizing.

Therefore the fixture must not test whether a profitable stop performs better. It must test only whether source evidence uniquely identifies the executable stop boundary.

## Synthetic case

Construct a bullish SP2L-like sequence with:

- a directional Spike;
- a clearly identifiable Spike-origin/base candle;
- a later structural correction level suitable for a pending Buy Limit;
- a deeper structural low near the Spike origin;
- an executable Entry distinct from the invalidation level.

Mirror the same construction for bearish research only where source evidence permits; absence of sufficient bearish evidence remains unresolved.

## Competing interpretations

### Candidate A — wick/base structural boundary

Stop/invalidation is anchored to the source-defined Spike-origin/base structural boundary using the relevant wick/extreme.

### Candidate B — body boundary

Stop/invalidation is anchored to the Spike-origin/base candle body boundary rather than its wick/extreme.

### Candidate C — generic opposite swing

Stop is derived from a generic opposite swing high/low selected by a conventional swing algorithm, independent of the source-defined Spike-origin/base semantics.

### Candidate D — risk-distance stop

Stop is calculated from Entry using a fixed distance, ATR-like distance, or risk-budget formula.

This candidate is a negative control: risk budget may determine position size after Entry and Stop Distance, but it must not define the Strategy A structural invalidation level without direct source evidence.

### Candidate E — source-defined buffer

A source-defined buffer/offset is applied beyond the structural invalidation boundary.

This candidate remains available only if direct source evidence explicitly establishes such a buffer. No pip, tick, ATR, percentage, or arbitrary one-tick buffer may be invented.

## Source-discrimination questions

1. Does the source uniquely identify the Spike-origin candle/index in every relevant variant?
2. Does it explicitly select wick/extreme versus body boundary?
3. Does it define a numerical or qualitative stop buffer?
4. Does it ever replace structural invalidation with a risk-distance calculation?
5. Does it establish a universal bullish/bearish mirrored rule?

## Expected adjudication

Current evidence is sufficient to reject risk-budget stop substitution and to retain structural invalidation as a distinct concept. It is not sufficient to uniquely select the exact OHLC field, wick/body boundary, universal candle index, or buffer.

Therefore the expected result is:

`SOURCE-DOES-NOT-DISCRIMINATE`

at the executable OHLC level.

If future Tier 1/Tier 2 source evidence explicitly resolves one of these dimensions, this fixture may be re-adjudicated. Until then, no candidate may be promoted to CANONICAL.

## Negative controls

Do not freeze any of the following without direct source evidence:

- `stop = Entry ± N`;
- fixed-pip stop;
- ATR-derived stop;
- risk-derived stop;
- arbitrary wick/body selection;
- arbitrary one-tick/pip buffer;
- generic swing-low/high substitution;
- assumed bearish mirror.

## Gate impact

- SOURCE RESOLUTION: partial pass; executable stop geometry remains unresolved.
- SYNTHETIC FIXTURES: F10 explicitly defined.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED for Strategy A geometry.
- UNTOUCHED VALIDATION: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: LOCKED.

## Governance

This document does not modify the deterministic engine, execution simulator, replay semantics, or production signal path. No backtest performance is used to choose among candidates. Manual approval by Ali is required before any source-confirmed rule can become CANONICAL.
