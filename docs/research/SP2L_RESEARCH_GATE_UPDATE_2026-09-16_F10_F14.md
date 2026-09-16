# SP2L Research Gate Update — F10 through F14 — 2026-09-16

## Completed in this pass

F10, F11, F12, F13 and F14 were cross-referenced against the source-aligned geometry records and existing deterministic fixture definitions.

## Current decisions

| Fixture | Source-supported boundary | Exact canonical geometry |
|---|---|---|
| F10 | Structural invalidation is distinct from risk budget | UNRESOLVED: OHLC anchor, wick/body, buffer |
| F11 | Pending Limit + qualitative refresh/update | UNRESOLVED: replacement threshold |
| F12 | 1/2/3-candle trigger family | UNRESOLVED: exact classifier |
| F13 | 2X second-position concept | UNRESOLVED: exact formula |
| F14 | Leg2 magnitude approximately equals Leg1 | UNRESOLVED: A/B/C/D + tolerance |

## Important result

No unresolved geometry was promoted to canonical during this pass.

The research state is therefore internally consistent with the source hierarchy:

`source semantics > fixture discrimination > implementation > performance`

## Gate

- Source Resolution: `PARTIAL PASS`
- Synthetic Fixtures: `PASS`
- Frozen Geometry: `BLOCKED`
- DEV: `LOCKED`
- Untouched Validation: `LOCKED`
- Robustness/Stability: `LOCKED`
- Fresh Holdout: `LOCKED`
- Production: `OFF`

## Next research targets

1. F15 bearish mirror/source confirmation.
2. Cross-reference P-Gap evidence against remaining source variants.
3. Verify the fixture suite in CI before relying on its execution status.
4. Maintain the 125R observation as an unresolved geometry case; do not filter it out.
