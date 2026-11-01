# SP2L V3 Exit Discovery — Status Snapshot

**Snapshot date:** 2026-11-01  
**Scope:** Strategy A V3 Entry / Exit Discovery and artifact-integrity remediation  
**Status:** Research-only; artifact audit implementation CI green; local evidence audit PASS (2026-11-01)  
**Checkpoint branch:** `research/checkpoint-v3-exit-discovery-20261101`  
**Checkpoint base commit:** `3deebf6e3c3c75e652aaa31f61fdd8f31b2aa3bc`

## 1. Workflow position

The completed 30-day M1 OHLC Discovery run is an exploratory, in-sample exit-management comparison using the frozen V3 entry population. It is not canonical, not a validated edge, and not a production selection. No entry geometry, P-Gap formula, AB=CD anchors/tolerance, fill semantics, or production execution rules are changed by this work.

Next required sequence:
1. Run the artifact audit against the preserved Windows artifacts.
2. Review the generated evidence manifest and verify every artifact/source hash and cross-file invariant.
3. Only then proceed to the next research stage; no candidate is promoted based on the exploratory ranking.

## 2. Discovery run and immutable inputs

Output directory:
`D:\Mirzaei\Private\1\sp2l-evidence\development\v3-exit-discovery-20261101`

Run prefix:
`SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z`

Expected artifacts:
- `SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z.json`
- `SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z_SUMMARY.csv`
- `SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z_TRADES.csv`
- `SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z_SNAPSHOT.md`

Discovery population:
- 462 frozen V3 entry signals.
- 288 exit variants.
- 133,056 trade replay rows.
- 29,919 M1 bars over the 30-day input window.
- 21 detected M1 gaps / 12,802 missing minute slots / largest gap 2,942 minutes.
- M1 gaps were not filled; open-trade gaps are classified ambiguous.
- OHLC proxy only; spread, slippage, and commission are not modeled.

Input sources:
- M1 CSV: `D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv`
- M1 SHA-256: `b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285`
- Frozen V3 entry CSV: `D:\Mirzaei\Private\1\xauusd-strategy-a-monthly-matrix-audit-worktree-20261024\artifacts\monthly_ohlc_activated_sensitivity_v3_20261024_162634_105\a_trail_0_40_activated_proxy_v3_trades.csv`
- Frozen entry SHA-256: `39ed87cd1f0be3e59b5f064b0bcf97a9787e5266df6e972aa07e5ea4d3608ab1`

The leading exploratory result previously observed was RR5_ACT15_D10: 461 decisive, 279 wins, 182 losses, 1 ambiguous, net +143.53R, PF 1.986, max drawdown 11.27R, and +$432.92. This is a discovery ranking only and is subject to in-sample/288-variant selection bias; it must not be treated as an approved exit configuration.

## 3. JSON/Snapshot hash discrepancy — resolved diagnosis

Preserved local artifact measurements:
- JSON actual on-disk SHA-256: `84dc52dc0019430e228c3cbacb23b5f4f947d4bc3179edbdc9c4eb8299ebab2c`
- JSON SHA-256 after CRLF-to-LF normalization: `8bad9942b904fb4c4ac93a78076bc7e0a24230e74bc629f7d0de9ac53f565786`
- Snapshot-recorded JSON SHA-256: `8bad9942b904fb4c4ac93a78076bc7e0a24230e74bc629f7d0de9ac53f565786`

The normalized hash exactly matches the value recorded in the Snapshot. The discrepancy is Windows text-mode newline translation, not evidence of changed JSON content. The original JSON, CSVs, and Snapshot must remain unchanged.

## 4. Code remediation

PR #378 — `[DRAFT] freeze V3 entry population and gate preserved M1 data for exit discovery`
- Branch: `research/m1-integrity-gate-v3-entry-freeze-20261101`
- Latest relevant commit: `5f808175a40fe52ba95512ce42258a3bccd77910`
- Generator now encodes JSON once, writes those exact bytes with `write_bytes()`, and hashes the same byte sequence.
- CI at the relevant commit: all four workflows passed (Full Repository Test Suite run 70; Factory Research Tests run 1793; SP2L forensic deterministic checks run 1058; Factory Journal Lock Cross-Platform Tests run 620).

PR #379 — `[DRAFT] audit V3 Discovery artifacts and write evidence manifest`
- Branch: `research/v3-discovery-artifact-audit-20261101`
- Latest tested commit: `3deebf6e3c3c75e652aaa31f61fdd8f31b2aa3bc`
- Audit records both raw on-disk JSON SHA-256 and LF-normalized JSON content SHA-256; Snapshot comparison uses the normalized content hash.
- Regression tests cover CRLF portability and rejection of an incorrect Snapshot hash.
- An initial full-suite run failed with 844 passed / 2 failed because the fixture Snapshot still used the raw hash. The fixture was corrected to bind the normalized hash.
- Latest CI on the corrected commit: all four workflows passed:
  - Full Repository Test Suite — run 74
  - Factory Research Tests — run 1803
  - SP2L forensic deterministic checks — run 1062
  - Factory Journal Lock Cross-Platform Tests — run 630

Both PRs remain Draft and unmerged. PR #379 is stacked on #378; its branch is one commit behind the current #378 base branch. Do not merge either PR as part of this checkpoint.

## 5. Local artifact audit — PASS

The user ran the corrected audit script from PR #379 against the preserved local Discovery run on 2026-11-01.

Reported result:
- Audit status: `PASS`
- Exit code: `0`
- Variants: `288`
- Frozen entry signals: `462`
- Trade rows: `133056`
- Local manifest:
  `D:\Mirzaei\Private\1\sp2l-evidence\development\v3-exit-discovery-20261101\SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z_EVIDENCE_MANIFEST.json`
- User-reported manifest SHA-256:
  `bea79456196e6e08b7186b1000eaec787d5ba6d697db0dd5c45bbb3322e49452`

The local manifest itself and its source artifacts were not uploaded to GitHub. The hash above is recorded as a user-reported audit receipt, not an independently re-hashed repository artifact. A separate receipt is stored at:
`docs/checkpoints/SP2L_V3_EXIT_DISCOVERY_LOCAL_AUDIT_RECEIPT_2026-11-01.md`

The audit PASS confirms artifact integrity and cross-file consistency only. It does not establish statistical significance, out-of-sample performance, execution realism, canonical exit geometry, or production readiness.

Preserve the current evidence files byte-for-byte. Do not regenerate Discovery, rewrite existing files, weaken integrity checks, merge PRs, place MT5 orders, or change Strategy A entry logic.

## 6. Explicit non-claims

- This snapshot does not certify a statistically validated edge.
- The best-ranked variant is not canonical or production-approved.
- OHLC replay is not tick-level broker execution.
- The current M1 gap treatment leaves some outcomes ambiguous.
- No Fresh Holdout has been run.


## 7. Robustness / stability audit implementation — CI PASS

A separate research-only implementation has been added on:
- Branch: `research/v3-exit-robustness-20261101`
- PR: #380 — [DRAFT] assess V3 exit robustness and 288-way selection bias
- Tested head commit: `eb6824c49e5f7b094f0c4c4b69903802021b750b`

Implementation:
- `scripts/audit_v3_exit_robustness.py`
- `tests/test_v3_exit_robustness.py`
- `docs/research/v3-exit-robustness-audit.md`

The audit verifies the Trades CSV raw SHA-256 against the local AUDIT=PASS manifest before analysis. It retains unresolved/open outcomes as non-decisive and never assigns them a synthetic return. It produces four equal-width chronological slices, local adjacent-grid neighbourhood diagnostics, and a circular moving-block max-t bootstrap across all variants using common resampled day blocks.

CI on tested head `eb6824c49e5f7b094f0c4c4b69903802021b750b`:
- Full Repository Test Suite — run 77: PASS; 850 tests passed.
- Factory Research Tests — run 1817: PASS.
- SP2L forensic deterministic checks — run 1065: PASS.
- Factory Journal Lock Cross-Platform Tests — run 644: PASS.

PR #380 remains Draft and unmerged. CI validates the implementation and tests, not the user's local run outputs or a statistical edge.

### Next local action

Run the robustness audit against the already-preserved local manifest and Trades CSV, writing only to a new output directory. Inspect the resulting report and CSVs before deciding whether any candidates are stable enough to freeze for later untouched validation. No Fresh Holdout has been consumed, and no candidate is canonical or production-approved.


## 8. Robustness runner correction — pending CI and local rerun

The first local execution exposed a `None` handling defect in daily aggregation. Follow-up commit `b3fb9b5e7b498b0cbe5adef6e719c78c5c2d2522` updates the daily matrix so any variant/day containing an ambiguous or unresolved outcome remains missing through the bootstrap; it is not imputed as zero. Days with no triggered rows remain zero-return days. Variants with fewer than three known daily observations are excluded from the max-t family and counted. Regression tests and research documentation were added. This follow-up has not yet been validated by CI or by a successful local robustness run; the prior CI PASS applies to the earlier implementation only. PR #380 remains Draft and unmerged.
