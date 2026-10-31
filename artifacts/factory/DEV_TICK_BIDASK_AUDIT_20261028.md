# DEV Tick Bid/Ask Dataset Audit — 2026-10-28

## Decision status

**Integrity and basic quote checks PASS; immutable Factory registration and adapter acceptance are NOT YET APPROVED.**

This report records the user-run, read-only PowerShell/Python audit output for the existing local artifact. The compressed raw dataset and manifest remain local/ignored and are not committed to Git. This report does not certify source geometry, execution semantics, tick-feed completeness, or a statistical edge.

## Dataset identity

- Role intended: `DEVELOPMENT` only
- Symbol: `XAUUSD.ecn`
- Server/provider in manifest: `OtetGroup-MT5` / Otet Group MT5
- Requested interval: `[2026-08-21T00:00:00Z, 2026-09-19T00:00:00Z)`
- Local artifact: `data/raw/ticks/xauusd-ecn-ticks-20260821_20260919.csv.gz`
- Manifest: `data/raw/ticks/xauusd-ecn-ticks-20260821_20260919.manifest.json`
- File size: 111,124,585 bytes; manifest size matches
- SHA-256: `412a535b8d5f0413f329e5fde8a1f851591ee83c95fc25af38b287d6170a1347`; manifest hash matches
- Header: `time_msc,time_utc,bid,ask,last,volume,flags`
- Data rows: 10,817,858; manifest count matches
- First tick: `2026-08-21T01:00:05.864Z`
- Last tick: `2026-09-18T23:57:56.609Z`

The requested window begins at 00:00Z, while the first observed tick is at 01:00:05.864Z. This report does not claim ticks exist before the observed first tick or that every expected market-open instant is represented.

## Integrity and field checks

| Check | Observed | Result |
|---|---:|---|
| GZIP/CSV full read | 10,817,858 data rows | PASS |
| Row count vs manifest | Equal | PASS |
| SHA-256 vs manifest | Equal | PASS |
| Byte size vs manifest | Equal | PASS |
| UTC parse/timezone errors | 0 | PASS |
| `time_msc` vs `time_utc` mismatches | 0 | PASS |
| Invalid numeric rows | 0 | PASS |
| Zero/missing Bid or Ask | 0 | PASS |
| Nonpositive Bid or Ask | 0 | PASS |
| Crossed quotes (`bid > ask`) | 0 | PASS |
| Valid non-crossed Bid/Ask rows | 10,817,858 | PASS |

## Timestamp and gap diagnostics

- Adjacent duplicate timestamps: 12,389.
- Adjacent out-of-order timestamps: 0.
- Combined count matches manifest: 12,389.
- Duplicate timestamp groups: 7,429.
- Groups with differing Bid/Ask values inside the same millisecond: 6,895.
- Gaps between adjacent rows greater than 60 seconds: 20.
  - 4 Friday-to-Monday gaps around 49.035 hours.
  - 15 recurring weekday gaps around 61 minutes.
  - 1 gap from `2026-09-07T21:36:11.547Z` to `2026-09-08T01:00:07.172Z`, around 3.399 hours.

These are observations, not a determination of cause or proof of full feed completeness. The raw row order is monotonic nondecreasing, but timestamps are not unique. Since many repeated-millisecond groups contain different quotes, do not sort, deduplicate, collapse, interpolate, or synthesize replacement rows as part of this audit.

## Quote-field interpretation

- Spread observed: minimum approximately 0.13, mean approximately 0.2055609243, maximum approximately 1.29 price units.
- `last = 0` in all 10,817,858 rows.
- `volume = 0` in all 10,817,858 rows.

The dataset therefore supplies usable Bid/Ask quote observations under these checks; the zero Last/Volume fields must not be interpreted as actual trade prints or traded volume. Any cost, fill, intrabar ordering, or same-millisecond event policy needs a separately reviewed execution contract.

## Preservation note

An interrupted reacquisition created the local file `data/raw/ticks/xauusd-ecn-ticks-20260821_20260919.csv.gz.partial` (observed size at inventory time: 9,598,278 bytes). It is not the audited artifact and must remain preserved until separately reconciled. The original compressed artifact and manifest were not changed by the read-only audit.

## Gate interpretation

- **Gate A — input existence/integrity/basic quote checks:** evidence materially advanced; immutable Factory registration/receipt is still pending.
- **Gate B — source meaning:** BLOCKED. Executable Strategy A geometry and semantics remain unresolved; this dataset audit does not close P-Gap executable geometry, F08/F10–F16, or fill/entry/exit questions.
- **Gate C — execution contract and adapter:** BLOCKED pending reviewed schema/semantics, approved bytes-to-observation adapter, synthetic fixtures, provenance/repeatability, malformed-input, cost, and no-external-read tests.
- **Gate D — genuine product research run:** BLOCKED until approved DEVELOPMENT inputs, source-confirmed/fingerprinted rules, adapter and execution contracts are available.
- Fresh Holdout begins at `2026-09-19T00:00:00Z` and remains untouched.

No canonical rule, strategy-performance result, production authority, or BUY/SELL decision is established by this report.
