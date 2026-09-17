# SP2L Recent 4-Week Acquisition Result — 2026-09-17

## Observed execution

User executed the research acquisition on the identified terminal:

- Terminal: `Otet Group MT5 Terminal`
- Server: `OtetGroup-MT5`
- Symbol: `XAUUSD.ecn`
- Timeframe: `M1`
- Requested interval: `2026-08-21T00:00:00Z` → `2026-09-17T23:59:00Z`

## Raw audit result

- Expected active bars under the current observed calendar: `27600`
- Returned bars: `26746`
- Missing expected timestamps: `854`
- Unexpected timestamps: `0`
- Unique timestamps: `true`
- Chronological: `true`
- Audit status: `AUDITED_FAIL`
- Artifact SHA-256: `2b4784a196cef45611b7811fbe034770ea5feb4d98ef603c5ba7002d8c8f4143`

## Missing-data pattern

The missing set contains three materially different patterns:

1. Repeated end-of-session omissions around `23:58`/`23:59` UTC on multiple weekdays.
2. A large September 7 block from `21:37` through `23:59` UTC.
3. A September 17 block from `12:28` through `23:59` UTC.

The September 17 block is especially important because the artifact retrieval timestamp was `2026-09-17T09:27:45Z`, while the requested interval extended to `23:59Z`. This creates a timestamp/provenance question that must be resolved before interpreting the missing block as a market/session gap.

## Immediate data-provenance gate

Do NOT run the SP2L strategy harness on this four-week artifact yet.

Before any strategy statistics are extracted, resolve the time basis of MT5 Python timestamps for this exact terminal/server/symbol. The diagnostic `scripts/mt5_timestamp_basis_diagnostic.py` was added for this purpose.

The diagnostic compares:

- Python current UTC time;
- Python local time;
- raw MT5 tick epoch;
- raw MT5 M1 bar epochs;
- UTC and local representations of those epochs;
- distance between the raw epochs and the current clock.

No timestamp shifting is performed by the diagnostic.

## Why this gate matters

The acquisition script currently converts MT5 bar epochs directly to UTC and labels them `Z`. That assumption must be independently verified for the exact environment before the resulting UTC boundaries can be used for session auditing.

This is a data-provenance issue, not a strategy-geometry issue.

## Current decision

- Four-week acquisition: `AUDITED_FAIL`
- Strategy test on this artifact: `BLOCKED`
- Historical session applicability: `UNRESOLVED`
- Timestamp basis: `REQUIRES DIAGNOSTIC`
- SP2L geometry: unchanged
- No P-Gap/AB=CD/fill/lifecycle rule changes
- Production: `NOT AUTHORIZED`

## Next command

After pulling the latest branch:

```powershell
git pull
python scripts/mt5_timestamp_basis_diagnostic.py
```

Return the complete JSON output. Do not modify the CSV or shift timestamps manually.
