# SP2L MT5 copy_rates_from Boundary Validation — 2026-09-21

## Scope

Research-only acquisition diagnostic. This checkpoint records deterministic boundary behavior observed from the local OTET MT5 terminal.

It does **not** define Strategy A geometry, does **not** promote P-Gap rules, and does **not** authorize trading.

## Tests

### Test A — Requested interval

- Symbol: XAUUSD.ecn
- Server: OtetGroup-MT5
- Timeframe: M1
- Requested: 2026-09-20T01:00:00Z → 2026-09-20T11:46:00Z
- Expected bars: 647
- Returned bars: 647
- Actual first: 2026-09-18T13:11:00Z
- Actual last: 2026-09-18T23:57:00Z
- Count match: PASS
- Boundary match: FAIL
- Chronological: PASS
- Unique timestamps: PASS
- One-minute continuity: PASS
- Overall: **FAIL**

The API returned a contiguous 647-bar sequence, but it was not the requested historical interval.

### Test B — Returned interval replayed as the request

- Requested: 2026-09-18T13:11:00Z → 2026-09-18T23:57:00Z
- Expected bars: 647
- Returned bars: 647
- Actual first: 2026-09-18T13:11:00Z
- Actual last: 2026-09-18T23:57:00Z
- Count match: PASS
- Boundary match: PASS
- Chronological: PASS
- Unique timestamps: PASS
- One-minute continuity: PASS
- Overall: **PASS**

## Finding

copy_rates_from can return the requested number of M1 bars while the returned sequence is anchored to a different historical interval. Therefore **bar-count equality is insufficient for historical interval validation**.

The explicit first/last boundary checks correctly detected the mismatch.

The second test confirms that the returned sequence itself is internally valid when its actual boundaries are requested.

## Gate status

- copy_rates_from internal sequence integrity: **PASS for observed returned sequence**
- Exact historical interval retrieval: **NOT VERIFIED**
- Boundary validation: **REQUIRED**
- Historical MT5 timestamp basis: **UNRESOLVED**
- API-vs-export equivalence: **PASS for 2026-09-21 window only**
- Strategy A Frozen Geometry: **BLOCKED**
- Canonical P-Gap executable geometry: **UNRESOLVED**
- Production: **DISABLED**

## Interpretation boundary

This evidence does not establish why the 2026-09-20 request resolved to the 2026-09-18 sequence. Possible causes include broker/terminal history availability, timestamp interpretation, or API retrieval semantics, but no cause is promoted without further evidence.

No timestamp shift, synthetic correction, parameter tuning, or geometry change is permitted to force alignment.

## Next gate

Use an independently available committed/exported MT5 interval whose exact OHLC boundaries are known, then perform a same-window API-vs-export comparison. Keep the raw timestamps unchanged and classify any discrepancy explicitly.
