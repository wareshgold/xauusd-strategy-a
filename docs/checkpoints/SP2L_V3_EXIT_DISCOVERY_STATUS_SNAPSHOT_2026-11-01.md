# SP2L V3 Exit Discovery — Status Snapshot

**Snapshot date:** 2026-11-01  
**Scope:** Strategy A V3 Entry / Exit Discovery and artifact-integrity remediation  
**Status:** Research-only; artifact audit implementation CI green; local evidence audit not yet run successfully  
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

## 5. Audit state and outstanding action

**No evidence manifest has yet been generated for the preserved local Discovery run.** CI validates the code and fixtures; it does not validate the user's local 133,056-row artifact bundle.

Next action is to run the audit script from the corrected PR #379 branch against the existing JSON file. It must:
- validate the M1 and frozen-entry source hashes and byte size;
- reconcile JSON matrix, Summary CSV, Trades CSV, embedded JSON trades, and frozen trade identities;
- validate Snapshot against the LF-normalized JSON content;
- write a new manifest only if the target does not already exist.

Preserve the current evidence files byte-for-byte. Do not regenerate Discovery, rewrite existing files, weaken integrity checks, merge PRs, place MT5 orders, or change Strategy A entry logic. If the audit fails, preserve the failure output and diagnose the specific invariant; do not force a PASS.

## 6. Explicit non-claims

- This snapshot does not certify a statistically validated edge.
- The best-ranked variant is not canonical or production-approved.
- OHLC replay is not tick-level broker execution.
- The current M1 gap treatment leaves some outcomes ambiguous.
- No Fresh Holdout has been run.
