# SP2L G48 — Real XAU/USD Acquisition

Date: 2026-09-09
Gate: G48
Status: IMPLEMENTED; LIVE RUN REQUIRED

## Objective

Validate the end-to-end, strategy-neutral acquisition path:

Twelve Data `/time_series` → raw preservation → raw SHA-256 → provider parsing → UTC normalization → quality audit → acquisition manifest → dataset artifact.

## Implementation

- `research/engine/acquire_xauusd.py` provides a local CLI.
- API credentials are read only from an environment variable and are never printed or written to source control.
- The raw HTTP response is preserved as `raw/time_series.json`.
- Normalized UTC candles are stored as canonical JSON in `normalized/candles.json`.
- Raw and normalized SHA-256 fingerprints are recorded.
- Source timezone is explicit and mandatory for naive provider timestamps.
- Quality failure returns a non-zero exit code and is recorded as `BLOCKED`.
- Acquisition and dataset manifests record provenance and quality state.

## Determinism boundary

The HTTP retrieval timestamp is provenance metadata and therefore varies between acquisitions. Dataset identity is anchored by raw and normalized fingerprints plus the recorded provenance. The acquisition runner does not infer Strategy A geometry and does not emit BUY/SELL decisions.

## Current provider configuration

- Provider: Twelve Data
- Instrument: XAU/USD
- Interval: 1min
- Sample size: 5000 by default
- Source timezone: explicitly supplied by operator; no local-machine timezone inference

## Acceptance

G48 becomes PASS only after a real API run produces a quality-audit PASS and a complete manifest/artifact pair. A CI pass alone does not constitute G48 data acquisition validation.

## Strategy boundary

This gate does not resolve P-Gap, Entry, Structural SL, Trigger, AB=CD, Leg2, or any other unresolved Strategy A geometry. Frozen Geometry remains blocked.
