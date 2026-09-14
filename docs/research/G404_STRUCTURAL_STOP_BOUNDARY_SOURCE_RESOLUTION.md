# G404 — Structural Stop Boundary Source Resolution

## Purpose
G404 addresses the remaining G400 blocker covering structural invalidation, stop boundary, and executable stop semantics.

## Source-first boundary
Existing research contains a G3 structural-stop candidate that places a bullish candidate at the spike-origin low and a bearish candidate at the spike-origin high, while leaving any buffer as TBD. That candidate is not canonical and does not resolve the G400 blocker.

G404 therefore does not freeze:

- which event/candle defines the stop reference;
- whether the boundary is a wick extreme, body boundary, or another source-defined level;
- which OHLC field is executable;
- whether a buffer exists or how it is measured;
- whether structural invalidation cancels a pending order before fill;
- whether structural boundary and executable stop price are identical.

## Research hypotheses
Six dimensions are explicitly kept non-canonical: stop reference, stop boundary, price field, buffer, invalidation timing, and executable stop mapping.

## Minimal-pair discrimination
Seven targeted pairs isolate:

1. spike-origin versus setup-boundary reference;
2. wick versus body boundary;
3. high/low versus open/close field;
4. zero versus positive buffer;
5. pre-fill versus post-fill invalidation;
6. structural boundary versus executable stop;
7. bullish versus bearish symmetry.

These fixtures are designed to identify distinctions supported by authoritative source wording or source visuals. They do not select a winner from profitability or convention.

## Evidence required
A status change requires traceable authoritative source material, source visual evidence, or a source-derived artifact with auditable provenance. Common stop conventions, implementation convenience, and profitable hypotheses are insufficient.

## Gate status
**UNRESOLVED / RESEARCH-ONLY**

G404 does not clear G400, does not authorize executable stop geometry, and does not authorize optimization or production deployment.
