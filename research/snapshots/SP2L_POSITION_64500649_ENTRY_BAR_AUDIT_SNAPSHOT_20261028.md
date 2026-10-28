# Evidence Snapshot — Position 64500649 Entry-Bar Trailing Audit

- Snapshot ID: `SP2L-POSITION-64500649-ENTRY-BAR-AUDIT-20261028`
- Recorded: 2026-10-28
- Repository: `wareshgold/xauusd-strategy-a`
- Research branch: `research/position-64500649-m1-boundary-audit-20261028`
- Baseline HEAD before snapshot commit: `9a572ad56392dc2794b07f57cbac170c6598e625`
- Related draft PR: [#363](https://github.com/wareshgold/xauusd-strategy-a/pull/363)
- Scope: read-only incident audit and deterministic offline replay only.

## Frozen incident facts supplied from MT5

- Symbol: `XAUUSD.ecn`
- Position: `64500649`, SELL, volume `0.01`
- Entry deal time: `2026-10-27T12:56:05.552Z`
- Entry price: `4006.11`
- Exit deal time: `2026-10-27T13:01:49Z`
- Exit price: `4013.06`
- Exit reason: SL (`reason=4`); closing comment `[sl 4012.95]`
- Initial order SL: `4012.95`; TP: `3992.40`
- No `TRAIL_UPDATE` event found for this position in the inspected event log.

## Tick and M1 evidence

- 12:56 M1 bar: O `4005.46`, H `4008.74`, L `4005.44`, C `4007.82`.
- The bar low `4005.44` occurred at `12:56:00.083Z`, about 5.469 seconds before entry.
- Minimum Bid from the precise entry timestamp onward in the queried tick range: `4006.06` at `12:56:06.140Z`.
- Post-entry favorable movement by this Bid diagnostic: `0.05`, below the configured research activation distance `0.40`.
- Minimum Ask observed in the following 12:57 minute: `4006.94`.
- The full entry-bar low would yield favorable movement `0.67` and candidate SELL SL `4005.84` under the inspected runner arithmetic.
- That candidate is below the observed 12:57 minimum Ask and therefore fails the runner's SELL Ask-distance guard throughout that observed minute, assuming the inspected guard and supplied data apply.

## Runner provenance

- Local runner path reported by user: `scripts/run_sp2l_v3_xauusd_forward_test.py`
- SHA-256 reported by user: `0FE5B67D33BC93D9A7244C79B951F91E9A00A616960C2AD6DFD4E292611DC873`
- The hash is a user-supplied local-file observation; it is not independently recomputed by this repository snapshot.

## Interpretation frozen at this point

- Demonstrated risk: a full M1 entry-bar low can include pre-entry price action and pass the activation arithmetic despite insufficient post-entry favorable movement.
- For this incident, the derived candidate SL would have failed the observed Ask-distance guard; no evidence shows a successful SL modification.
- Missing `TRAIL_UPDATE` does not identify which pre-send guard prevented a request or prove exact polling timing.
- This is a single-position diagnostic. It does not establish strategy-wide performance or define canonical Strategy A geometry.

## Integrity and safety boundaries

- Snapshot records facts and conclusions as known at this point; later findings must be added in a new snapshot or explicitly versioned addendum, not silently rewrite this one.
- No live runner, MT5 state, event log, or trading configuration was changed by the audit.
- No canonical rules were created or changed.
- Validation reported green for both repository workflows on baseline commit `9a572ad56392dc2794b07f57cbac170c6598e625` before this snapshot commit.
