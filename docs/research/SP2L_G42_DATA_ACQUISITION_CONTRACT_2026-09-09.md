# SP2L G42 — Data Acquisition Contract

Date: 2026-09-09

## Gate

Strategy-neutral data acquisition and provider provenance.

## Objective

Create a reproducible path from a named market-data provider to immutable raw XAUUSD M1 research artifacts without selecting, modifying, or optimizing Strategy A geometry.

## Current provider candidate

**Twelve Data — XAU/USD commodity aggregate** is the initial acquisition candidate, not a canonical market-data authority.

Current official provider documentation identifies XAU/USD as a supported Gold Spot / US Dollar commodity aggregate and exposes intraday time-series data including 1-minute intervals. The provider also documents a commodity default timezone and allows timezone selection in requests. Exact coverage for the requested historical window must be recorded from the actual acquisition response rather than inferred from marketing/reference pages.

## Acquisition request contract

Each acquisition must record:

- provider name;
- provider instrument identifier (`XAU/USD` for the candidate);
- requested interval (`1min` for raw research candidate);
- requested UTC start/end;
- request/retrieval timestamp in UTC;
- provider timezone returned/used;
- provider source/version metadata when available;
- pagination/chunk boundaries;
- response count;
- raw response fingerprint;
- normalized dataset fingerprint.

API credentials must be supplied through runtime secrets and never committed to Git.

## Raw-source rule

The first stored artifact is the provider response or a byte-for-byte canonical serialization of it. No missing bars may be fabricated. No provider-specific candle may be replaced with another feed's value during ingestion.

Normalization is limited to:

1. parsing the provider timestamp;
2. applying the explicitly recorded provider timezone when the timestamp is naive;
3. converting timestamp representation to UTC;
4. converting numeric OHLC fields into the canonical internal numeric representation;
5. retaining provider metadata.

## Coverage verification

Before a dataset can enter DEV research, verify from the acquired data itself:

- requested start/end are covered;
- actual first/last timestamps are recorded;
- row count is recorded;
- timestamp cadence is audited;
- duplicates are counted;
- gaps are counted and listed;
- OHLC integrity passes;
- symbol/interval metadata matches the request;
- incomplete acquisition chunks are explicitly marked.

A provider page claiming historical coverage is not sufficient evidence that a specific requested dataset was actually delivered.

## Feed comparison boundary

If a second feed is added (for example TradingView/broker data), it must be stored as a separate provider dataset. We must measure timestamp alignment, price deviations, missing bars, and candle-construction differences before treating feeds as interchangeable.

No feed may be selected because it produces better Strategy A backtest results.

## Reproducibility artifact

Every acquired dataset must have:

`provider + instrument + interval + UTC bounds + row count + source metadata + raw fingerprint + normalized fingerprint`

and must be reconstructable without access to the developer's personal computer.

## Production boundary

G42 does not authorize historical Strategy A BUY/SELL detection. Frozen Geometry remains blocked under G40. Data acquisition is infrastructure only.

## Acceptance criteria

- [ ] provider adapter parses real provider-shaped payloads;
- [ ] timezone is explicit and never guessed from the local machine;
- [ ] provider errors fail loudly;
- [ ] raw and normalized fingerprints are recorded;
- [ ] requested vs actual coverage is measurable;
- [ ] missing/duplicate bars are explicit;
- [ ] credentials are external to the repository;
- [ ] a second feed can be added without changing canonical Strategy A code;
- [ ] no Strategy A geometry is imported into the adapter.

## Next gate

Acquire a small real XAU/USD M1 sample, store its immutable provenance manifest, run the quality audit, and only then scale to the DEV historical window.
