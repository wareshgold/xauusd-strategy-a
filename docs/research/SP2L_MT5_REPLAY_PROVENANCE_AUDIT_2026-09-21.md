# SP2L MT5 / Replay Provenance Audit — 2026-09-21

## Replay determinism
`src/backtest/ReplayEngine.ts` exposes only candles from index 0 through the current replay index. No future candle is exposed to the handler. This provides a basic no-lookahead invariant for replay consumers.

## Historical dataset integrity
`scripts/audit-dataset.mjs` checks:
- duplicate timestamps;
- chronological ordering;
- OHLC validity;
- expected timeframe gaps;
- suspicious non-weekend-like gaps;
- source/timezone metadata.

## MT5 provenance boundary
MT5 acquisition evidence remains broker-terminal-specific:
- symbol: XAUUSD.ecn;
- server: OtetGroup-MT5;
- terminal timestamps are not yet historically proven to be UTC;
- session calendar is terminal-time based;
- recurring broker/session gaps exist.

Therefore MT5-derived datasets must retain raw terminal timestamps and provenance metadata and must not silently be converted into canonical UTC without an explicit verified mapping.

## Session rule
The previously established historical research rule remains:
- stored historical canonical timestamps: UTC;
- London evaluation: Europe/London;
- New York evaluation: America/New_York;
- DST handled by IANA zones;
- Iran/local time is display/context only.

This does not establish a Strategy A entry/exit rule.

## Guardrails
- No lookahead through ReplayEngine.
- No silent timestamp reinterpretation.
- No missing-bar interpolation without provenance.
- No session filtering used to select unresolved geometry.
- MT5 data quality issues remain auditable rather than hidden.

## Gate
- Replay provenance: PASS (basic no-lookahead invariant)
- Dataset integrity tooling: PRESENT
- MT5 historical timestamp mapping: UNVERIFIED
- Session provenance: RESEARCH-ONLY
- Frozen Geometry: BLOCKED
- Production: DISABLED
