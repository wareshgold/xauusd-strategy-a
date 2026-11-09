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


## Verification follow-up (2026-11-09)

- Local isolated-worktree validation completed: `ENGINE_PATH` resolved inside `xauusd-strategy-a-trailing-anchor-review\src\strategy_factory\v3_management_engine.py`; focused test command completed with **13 passed**.
- The local execution worktree was at commit `1d1b29e79e7b2a0305e066bcf5122ce98d9f375e` in detached-HEAD state (empty `git branch --show-current`). The remote research branch subsequently contains one documentation-only commit, `03b8a27236c3eb199795625a779f15ba5053e888`; that commit changes only this snapshot.
- Local Git blob hashes match the branch's current code blobs:
  - Engine: `e4601bea40672a52303d62ff5ec966e9035c1f92`
  - Comparison runner: `83da8c8d56952c097a9b46e89cd4a34ddf54f956`
  - Frozen-input loader: `a4b4cbeee3026868264d0269f05c4f34cc1feba7`
- The output directory's manifest SHA256 matches the reported value `52e14660dc5fa214a9d20849d413c49782696b12ba5f9dbec4647d6f3c17df91`. All three artifact hashes recorded in the manifest independently match the files on disk:
  - SUMMARY.csv: `f9ec5e0108e19937f04a123663ba86bddec3b92653b1f95fd036437f0a77a21`
  - TRADES.csv: `54f8e60e22b139603baeb489cc1cbaf8ee4afc59f6a5648d7568e3debe47fea4`
  - PAIRED.csv: `294c1fae3553a7fa2af8fb1c325d6b34401bc8f087b97c6acb2f90000786e30d`
- Frozen input hashes in the manifest match the expected M1 and entry-population hashes.
- **Provenance limitation remains:** the run manifest does not record the Git commit or code blob hashes at execution time. Current code identity and test/import correctness are verified, and artifact integrity is verified, but this does not independently prove which code bytes were loaded during the historical replay. Therefore the reported metrics remain **provisional research evidence**, not a fully provenance-closed result.
- No replay was rerun; no MT5/Runner was accessed; no PR was merged.

## Provenance-closed rerun preparation (2026-11-09)

- Updated `scripts/run_sp2l_trailing_anchor_comparison.py` to capture execution provenance before loading the frozen inputs and before replay begins.
- The new manifest field `execution_provenance` records Git root, HEAD, branch, complete porcelain worktree status, dirty flag, SHA256 of the diff against HEAD, and SHA256/path for the exact comparison runner, imported matrix loader, and imported management engine source files.
- It also records Python executable/version, platform, and exact command-line arguments.
- The capture is made inside the replay process, after Python imports resolve and before any replay is performed. This closes the prior missing evidence about the source files and repository state used by the run, subject to the normal assumption that those source files are not modified during execution.
- The script still refuses output-directory overwrite. The rerun must use a new unique output directory; the prior `DIAG_ANCHOR_CANONICAL_20261109_150521` remains untouched.
- This commit only prepares the runner. **No replay has been executed here** because the frozen M1/entry files and local Windows worktree are not mounted in this environment. No MT5/Runner access, no PR merge, and no canonical selection.
- Rerun acceptance gate: verify manifest contains non-null `git_head`, exact source-file hashes, `git_worktree_dirty=false` (or explicitly review a dirty state), and unchanged frozen input hashes before comparing metrics with the provisional run.


## Provenance-closed replay — verified operator report (2026-11-09)

Output directory:
`DIAG_ANCHOR_PROVENANCE_20261109_153230`

- Execution HEAD: `1a5f85d02874509074eeb20df28e28706b5c5e9c` (detached HEAD; branch field empty by design for the detached worktree).
- Worktree status: dirty only because Python generated untracked `src/strategy_factory/__pycache__/*.pyc` files. `git diff --name-only HEAD` was empty and the diff SHA256 was the SHA256 of an empty byte stream: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`. No tracked source files were modified.
- Exact loaded source SHA256 values recorded in the run manifest:
  - Comparison runner: `ee45c57c5e28d889662cb5342c04391611f714d8a7772201bf3ca25e169cd26e`
  - Frozen-input matrix loader: `ed01d603d4a8736802241b55b78e6dfe750ac96fa61dbeb33bc56049990ef772`
  - Management engine: `d7479575ad7f1689b4943932850f23b8a5bde1480419d9f1961538c7b9959b61`
- Frozen input hashes match the baseline above: M1 `B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285`; entries `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`.
- Manifest SHA256: `36EEC32688C1E399C57C14C681B8CAE0C61F84E45F9BB8F066EE895DAECDFE4C`.

| Profile | Decisive | Wins | Losses | Breakeven | Ambiguous | Open | Gap-exposed | Net R | Gross USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RR4_CANDLE | 461 | 325 | 135 | 1 | 0 | 1 | 0 | 153.2532206 | 439.69 |
| RR4_CUMULATIVE | 460 | 327 | 133 | 0 | 1 | 1 | 1 | 140.7877514 | 379.19 |
| NO_TP_CANDLE | 461 | 323 | 137 | 1 | 0 | 1 | 0 | 152.4809289 | 433.78 |
| NO_TP_CUMULATIVE | 460 | 325 | 135 | 0 | 1 | 1 | 1 | 141.7862445 | 375.31 |

- Results reproduce the earlier canonical replay metrics to the displayed precision.
- Candle versus Cumulative gross difference: +$60.50 for RR4 and +$58.47 for NO_TP, in favor of Candle anchoring.
- These are gross, pre-cost research results. Spread, commission, slippage, broker stop/freeze restrictions, and tick-level bid/ask execution are not modeled. One open trade remains in each profile; cumulative profiles each have one ambiguous and one gap-exposed outcome.
- The untracked cache files explain `git_worktree_dirty=true`; the tracked source tree was clean. No replay rerun is required to explain this status.

## Research decision and next gate

- The provenance-closed replay is accepted as reproducible offline evidence for this frozen sample. Candle anchoring is the current research leader, not a canonical or production selection.
- **Do not promote this result to canonical and do not tune further on this same sample.** Next gate is a separately identified Fresh Holdout with a pre-registered comparison protocol, locked before any holdout outcomes are inspected.
- Holdout protocol must specify the anchor variants, management settings, entry population/data window and hashes, treatment of open/ambiguous/gap-exposed trades, costs/execution assumptions, primary metric, paired statistical test, and acceptance/rejection thresholds in advance. Holdout must remain untouched until that protocol is frozen.
- No MT5/Runner/dashboard access or changes; PR #414 remains untouched and unmerged.
