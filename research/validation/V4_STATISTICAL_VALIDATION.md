# V4 Statistical Validation Protocol and Results

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Candidate:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z`  
**Conclusion:** `NOT_PROVEN` (diagnostic only; costed executable edge test is blocked).

## Frozen protocol

The V4 design was recorded in `research/design/V4_DESIGN_FREEZE.md` before the replay. Baseline and candidate share the research V3 signal definition, candidate ordering and data. The only registered difference is exits: V3 research proxy TP=2R plus 0.40-price-unit trailing after +0.40 favorable move, versus V4 hypothesis TP=1R/no trailing. It is not a canonical strategy change.

Frozen data split:

- Development week: 2026-07-06 through before 2026-07-13 UTC.
- Development month: July 2026.
- Validation month: August 2026.
- Fresh holdout diagnostic: available September 2026 data through 2026-09-17 (manifest interval end).

No parameter sweep was performed. Holdout was not used to tune settings. One research alternative was registered. Seed 20261028; 2,000 day-cluster bootstrap resamples for mean daily gross R. The interval is conditional on this data, the proxy signal definition, and event assumptions; it is not corrected for data-quality or execution uncertainty.

## Integrity gate and data coverage

Actual CSV hashes do not match their acquisition manifests; all three full-period data runs therefore have `data_integrity_status=FAIL` and row status `BLOCKED`:

| Dataset | Rows in file | Manifest returned / expected | Manifest audit | Declared SHA256 | Actual SHA256 | Gaps >60 sec |
|---|---:|---:|---|---|---|---:|
| July 2026 | 31,483 | 31,483 / 31,740 | AUDITED_FAIL | `482991df85c7143077ef3713c81f3c5ae14ae12311f6c03e3579f27f8048e34e` | `0215c22898ac5b867bd51096cbbe59e50d0623597eb64aa56d9937c9088f4936` | 22 |
| August 2026 | 28,957 | 28,957 / 28,980 | AUDITED_FAIL | `8d9f4d9a82ff2fcbedfc8221ef62da1b4c518d037a000f09b8ec888077ca4a87` | `c7bac957eba4e4c2b8606c19913b25dec7b6c71adcda7fbfac3992d362c8eac7` | 20 |
| September 2026 (available) | 17,069 | 17,069 / 17,940 | AUDITED_FAIL | `3b7212dc43f844807da120d89e6cbae9f63def4943fefdb003c54d630467cc2b` | `1bb2dcdc163e13fa08487c5d7a68905325e9be50104a57aedbe0bbde7055f1d4` | 12 |

All acquisition manifests say historical session-calendar applicability `UNVERIFIED`; manifests list timestamp gaps and historical retrieval context. Session closures vs missing bars cannot be reclassified from this evidence. No rows were filled or interpolated. A path reaching a data gap without resolved exit is censored, not assigned a favorable or adverse price.

## Observed diagnostic outcomes (gross, not costed)

The runner emitted paired baseline/V4 rows for all four periods. These outcomes are deliberately not a performance claim because input hashes fail, the theoretical trigger-bar extreme is not an executable fill, costs were not applied, and high-frequency OHLC path is ambiguous.

| Period | V3 proxy decisive n / expectancy R | V4 decisive n / expectancy R | V4 gross PF | V4 ambiguous / censored | V4 bootstrap 95% CI (mean daily gross R) | Common / baseline-only / V4-only signal keys |
|---|---:|---:|---:|---:|---|---|
| July 6–10 week | 2 / -1.000 | 100 / +0.240 | 1.632 | 0 / 1 | [3.8, 5.8] | 101 / 7 / 0 |
| July month | 15 / -1.000 | 424 / +0.222 | 1.570 | 2 / 2 | [2.435, 5.696] | 428 / 28 / 0 |
| August month | 15 / -1.000 | 479 / +0.290 | 1.818 | 6 / 6 | [4.905, 8.333] | 491 / 41 / 0 |
| September available holdout | 15 / -1.000 | 280 / +0.236 | 1.617 | 6 / 4 | [2.769, 7.615] | 290 / 21 / 0 |

The baseline proxy shows excessive ambiguous same-bar stop/TP/trailing paths (441 July, 517 August, 296 September); these are not decisive and are excluded from the baseline expectancy. As a result the baseline denominator is only 2 decisive trades in the week and 15 in each month. This is a model limitation and blocks statistical comparison. V4 OHLC signal and exit proxy also has an optimistic theoretical entry convention; overlap filtering differs by exit duration, with V4-only signals zero because both use identical signal timestamps and V4’s shorter duration simply admits additional common signals that baseline is still holding.

These numbers are included to preserve adverse and favorable diagnostics, not to rank or select a strategy. No trade-level reconciliation demonstrates actual broker fills; no transaction cost estimate is trustworthy; no live forward outcome is used as a controlled execution backtest.

## Required interpretation

- **Fresh holdout:** was run once as the pre-frozen September diagnostic, not used for selection; it is not a valid untouched confirmatory holdout because the acquired dataset fails declared-hash verification and its session calendar is unverified. Record as `BLOCKED / NOT_VALIDATED`, not as confirmation.
- **Sample size:** V4 has 100+ decisive proxy outcomes in the month/holdout; but sample count does not repair invalid data, fill semantics or missing costs. Baseline’s 15 decisive outcomes/month and 2 in the one-week slice are inadequate for paired inference.
- **Costs:** spread/commission/swap/slippage absent; net-after-costs is `NOT_TESTED` (CSV spread units do not resolve price-cost conversion). No speed/edge claim.
- **Robustness:** month/week comparisons exist, but regimes, parameter perturbation, spread/slippage/delay stress, trailing-only alternatives, session/trend filter variants and timestamp manipulations were not run or cannot be evaluated from current evidence. These requirements remain `NOT_TESTED` or `BLOCKED` in coverage.
- **Multiple comparisons:** one V4 alternative registered, no search/optimization. Existing historical research artifacts are not pooled into this test.
- **Decision:** gross diagnostics differ materially but are not evidence of a repeatable statistical edge. V4 is `NOT_PROVEN`; any performance claim must wait for reconciled immutable data, validated execution-cost/fill model, adequate paired baseline sample, and a new untouched holdout after any changes.
