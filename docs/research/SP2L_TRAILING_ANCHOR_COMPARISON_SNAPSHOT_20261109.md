# SP2L Trailing Anchor Comparison — Research Snapshot

**Date:** 2026-11-09  
**Status:** research-only; no canonical selection; no MT5/Runner access.

## Frozen baseline
- Repository: `wareshgold/xauusd-strategy-a`
- Base commit: `e62f5a159718b0398a2d2672858e0a6c4247ebbc`
- Existing matrix PR: #414 remains open/unmerged and is not modified by this snapshot branch.
- M1 input SHA256: `B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285`
- Frozen entry population SHA256: `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`
- Population: 462 entries; M1: 29,919 bars.

## Prior diagnostic comparison
Output directory:
`DIAG_ACT40_TRAIL40_COMPARE_20261109T112353Z`

Paired rows: 460  
Different outcome/time/reason: 128  
Mean MATRIX-minus-PROXY delta R: +0.0257

This diagnostic was a custom simplified replay, not the canonical engine and not a faithful broker/Runner simulation. Its aggregate metrics are not decision-grade.

## Forensic trade traces
### Population index 311 — SELL
- Entry 4085.44; initial SL 4088.43; risk 2.99.
- Candle-anchored model deferred multiple proposed SLs because the SELL stop was not above candle close.
- At epoch 1792003620 it accepted SL 4084.05 (close 4083.66); next bar hit it.
- Cumulative model retained best favorable low, proposed 4079.96 repeatedly, and could not validate it until epoch 1792004520; it then accepted 4074.15 and exited later.
- This explains the diagnostic outcome difference for this trade.

### Population index 415 — BUY
- Entry 4133.05; initial SL 4128.18; risk 4.87.
- Candle-anchored model accepted SL 4140.61 at epoch 1792607400 (close 4140.62); next bar hit it.
- Cumulative model retained best favorable high and repeatedly proposed 4140.92 while close remained below that level. No stop update occurred before the initial SL was hit at epoch 1792611420.
- This explains the diagnostic outcome difference for this trade.

## Confirmed semantic issue
The two tested anchor definitions are not equivalent:
1. **Candle-Anchored:** proposed stop is derived from the current completed candle high/low.
2. **Cumulative-Anchored:** proposed stop is derived from the best favorable high/low since entry.

Both currently use a close-side validity check in the diagnostic. A stop can remain deferred when its proposed level is not on the valid side of close. The cumulative anchor can therefore preserve a stop level that is temporarily impossible to submit, while the candle anchor can later propose a different, valid level.

## Next work — do not skip
1. Implement a formal fixed-price adapter over the canonical management replay engine: per trade, `activation_r = 0.40 / risk`, `distance_r = 0.40 / risk`. Preserve the frozen inputs and canonical M1 gap handling.
2. Add an explicit anchor mode to the engine: `CANDLE` and `CUMULATIVE`. Keep stop update effective from the next bar.
3. Define and test identical ordering for SL/TP checks, stop validity, and deferred retries across both modes. No hidden fallback to a different anchor.
4. Add focused tests for trade indices 311 and 415, including the exact activation/defer/update sequence, then run the full 462-entry paired replay.
5. Keep broker-side constraints, bid/ask, spread, commission, slippage, and tick-level fills explicitly unmodeled unless their evidence and semantics are supplied.
6. Do not select a winner or call this Runner-equivalent until the canonical replay and source-level Runner comparison are complete.

## Safety boundary
- Offline research only.
- Do not initialize or query MT5.
- Do not restart, configure, or modify the live Runner/dashboard.
- Do not merge PR #414 or this research branch without explicit approval.


## Implementation progress (2026-11-09, follow-up)
- Added explicit `anchor_mode` validation to canonical `TRAILING_R` and `BREAK_EVEN_TRAILING` specs; accepted values are `CANDLE` and `CUMULATIVE`.
- Added per-trade fixed-price adapter `fixed_price_trailing_spec`: activation and distance are converted independently using the trade's frozen initial risk.
- Cumulative anchor tracks best favorable high/low since entry; candle anchor uses current completed bar high/low. Existing canonical close-side validity, next-bar stop activation, SL/TP same-bar ambiguity, and M1 gap detection are retained.
- Added unit tests for fixed-price conversion, anchor-mode validation, and a synthetic case where candle anchoring can update while cumulative anchoring remains deferred.
- Added offline comparison runner: `scripts/run_sp2l_trailing_anchor_comparison.py`.
  - Executes four paired profiles: RR4+CANDLE, RR4+CUMULATIVE, NO_TP+CANDLE, NO_TP+CUMULATIVE.
  - Uses the canonical frozen-input loader and `replay_management_trade`, with ACT=$0.40 and distance=$0.40 by default.
  - Produces SUMMARY.csv, TRADES.csv, PAIRED.csv, MANIFEST.json, SHA256SUMS.txt in a new output directory; refuses overwrite.
  - Costs and broker stop/freeze constraints remain explicitly unmodeled.
- Remote code is not yet locally tested. The next gate is local isolated worktree test execution, then the 1,848 canonical replays (4 profiles × 462 entries).
- No local worktree, live runner, MT5, or PR #414 was modified.


## Canonical replay results received (2026-11-09)
Output directory reported by local operator:
`DIAG_ANCHOR_CANONICAL_20261109_150521`

Manifest SHA256 reported:
`52e14660dc5fa214a9d20849d413c49782696b12ba5f9dbec4647d6f3c17df91`

| Profile | Net R | PF | Max DD USD | Ambiguous | Open |
|---|---:|---:|---:|---:|---:|
| RR4_CANDLE | 153.2532206 | 2.5887624 | 17.98 | 0 | 1 |
| RR4_CUMULATIVE | 140.7877514 | 1.8466330 | 18.85 | 1 | 1 |
| NO_TP_CANDLE | 152.4809289 | 2.5580619 | 17.98 | 0 | 1 |
| NO_TP_CUMULATIVE | 141.7862445 | 1.8348757 | 18.85 | 1 | 1 |

Paired outcome changes: RR4=147/462; NO_TP=148/462.

**Interpretation boundary:** these are reported offline engine outputs before test-collection was fixed. The accompanying pytest attempt failed during import, so treat metrics as provisional until the isolated worktree is explicitly forced onto Python's import path and the focused tests pass. No canonical method selection.

## Test collection failure — diagnosis
The traceback imports `strategy_factory` from the original checkout:
`D:\\Mirzaei\\Private\\1\\xauusd-strategy-a\\src\\strategy_factory\\__init__.py`
rather than the isolated review worktree. The reported syntax error is in that original checkout's `strategy_comparison.py`; the corresponding branch file fetched from GitHub is syntactically normal in the reported area. Likely cause: the shared virtualenv's editable-install path takes precedence because the worktree's `src` directory was not explicitly prepended to `PYTHONPATH`.
Next gate: run pytest with `PYTHONPATH=<review-worktree>\\src` and confirm the imported module path points inside the review worktree. Do not modify the original checkout to work around this.
