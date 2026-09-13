# G385 — DEV Readiness

## Current gate

**CANONICAL DEV: BLOCKED**.

Reason: frozen executable Strategy A geometry is not resolved. This remains a source-resolution constraint, not a data-science parameter to optimize away.

## Infrastructure findings

1. A Twelve Data downloader already exists and requests XAU/USD at 1-minute and 5-minute intervals.
2. The downloader requires `TWELVE_DATA_API_KEY` and stores UTC datasets under `data/historical/`.
3. A historical dataset audit workflow exists, but its current branch trigger targets an older research branch and therefore does not automatically validate G385 data changes.
4. The current G385 branch does not contain a verified historical XAUUSD dataset snapshot.

## Safe next move

- keep raw-data acquisition separate from canonical strategy execution;
- retarget/adapt the dataset audit workflow to the active research branch only after verifying its current file SHA;
- run the refresh only when the required API secret is actually available;
- record provider, instrument, timeframe, timezone, coverage, snapshot identity and audit output;
- do not run or publish canonical profitability results until frozen geometry is resolved.

## Promotion rule

A successful dataset audit establishes **data readiness only**. It does not authorize Strategy A DEV.
