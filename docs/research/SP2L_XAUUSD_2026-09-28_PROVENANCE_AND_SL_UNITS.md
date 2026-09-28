# SP2L XAUUSD 2026-09-28 research provenance checkpoint

Date: 2026-09-28
Branch: `research/sp2l-clean-forward-xau-eurusd-usdjpy-20260928`
HEAD: `25a6bdd03091d93e071b4146ad44271e5f9e4f73`

## Findings

1. The active clean-forward manifest is still research-only and must not be changed by this checkpoint.
   - XAUUSD.ecn: pGapPrice=1.0, spikeMultiplier=1.5, maxSlPrice=10.0, tpR=1.0.
   - EURUSD.ecn: pGapPrice=1.0, spikeMultiplier=1.5, maxSlPrice=10.0, tpR=1.0.
   - USDJPY.ecn: pGapPrice=1.0, spikeMultiplier=1.5, maxSlPrice=10.0, tpR=1.0.
   - Forward process remains an observation process; no canonical promotion.

2. The current MT5 discovery matrix runner interprets `max_sl_distance` as a PRICE DISTANCE, not a pip count. Therefore passing `20,30,40,50` directly would be incorrect for XAUUSD.

3. Existing repository artifact `artifacts/backtest-multi/SP2L_fixed_sltp_matrix_full_history.json` explicitly records the project pip conventions:
   - `REPO_PIP_0.01`: XAUUSD.ecn pip size 0.01.
   - `PRACTICAL_GOLD0.10_IDX1.0`: XAUUSD.ecn pip size 0.10; marked as the headline/practical convention.
   This artifact is a synthetic fixed-SL/TP experiment and does NOT redefine Strategy A SL geometry.

4. Under the existing practical gold pip convention, a research sensitivity range of 20-50 pips corresponds to PRICE distances 2.0-5.0:
   - 20 pips -> 2.0 price
   - 30 pips -> 3.0 price
   - 40 pips -> 4.0 price
   - 50 pips -> 5.0 price
   These are research values only. They are not canonical Strategy A rules.

5. The previously quoted 62.25% XAUUSD result (222 signals / 204 decisive / 127 wins / 77 losses / +50R / max DD 6R) was NOT recovered as a committed artifact on the current branch or its immediate clean-forward history. The repository does contain:
   - 2026-09-14..18 author-replica result: 38 signals, 27 wins, 10 losses, 1 ambiguous, 72.973% decisive WR.
   - 4-week author-replica baseline: 158 signals, 103 wins, 51 losses, 4 ambiguous, 66.883% decisive WR, +52R.
   These are distinct results and must not be substituted for the 62.25% claim.

6. No new discovery matrix was run in this checkpoint. The earlier guessed 81-row-per-symbol matrix is therefore not treated as evidence for or against Strategy A.

## Decision boundary

Until the exact 62.25% run provenance (artifact or exact command + code/version + data window + outcome semantics) is recovered, it must remain HISTORICAL_UNVERIFIED and cannot be used to select or freeze a forward configuration.

The next research matrix, once provenance recovery is complete, may use the explicitly documented 20/30/40/50 pip sensitivity range as 2.0/3.0/4.0/5.0 price units for XAUUSD.ecn. This matrix must remain descriptive and must not select a canonical winner.

## Safety

Do not change or restart the currently running forward test as part of this checkpoint.
