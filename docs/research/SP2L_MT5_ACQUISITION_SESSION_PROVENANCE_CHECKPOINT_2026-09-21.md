# SP2L MT5 Acquisition / Session Provenance Cross-Window Checkpoint — 2026-09-21

## Scope
Consolidates the existing MT5 acquisition, session-calendar, availability, and timestamp-alignment evidence.

## Reproducible observations
- Terminal/server environment: Otet Group MT5 Terminal / OtetGroup-MT5.
- Target symbol: XAUUSD.ecn.
- M1 acquisition and raw session-availability tooling exist.
- Raw MT5 timestamps are preserved without normalization.
- Session availability can be measured from raw terminal-returned timestamps.
- Recurring availability gaps are observable and must not be silently treated as trading-session definitions.

## Timestamp mapping
Observed diagnostics show a consistent offset-like relationship between terminal-returned timestamps and Python UTC observations in the tested environment, but the historical basis is not independently proven as a fixed UTC offset.

Therefore:
- no hard UTC offset is frozen;
- no historical conversion rule is promoted;
- terminal timestamps remain the source-of-record for this audit layer.

## Session matrix
The matrix may report:
- weekday;
- terminal-time hour bucket;
- raw availability;
- gap boundaries.

It may not label those buckets as canonical London/New York sessions until timestamp mapping is independently verified.

## Data integrity guard
No missing-bar interpolation, silent timezone conversion, or session inference from gaps is permitted.

## Strategy isolation
This work does not modify P-Gap, F08-F15 geometry, entry, stop, fill, or production execution rules.

## Gate
- MT5 acquisition tooling: PRESENT
- Raw availability audit: PRESENT
- Cross-window timestamp evidence: OBSERVED BUT NOT HISTORICALLY VERIFIED
- Canonical UTC mapping: BLOCKED
- Session trading use: BLOCKED
- Frozen Geometry: BLOCKED
- Production: DISABLED

## Next required evidence
An independent, reproducible terminal/server timestamp reference is required to close the historical time-basis gate. Until then, MT5 data may be used for raw-data diagnostics but not as a canonically session-normalized production validation source.
