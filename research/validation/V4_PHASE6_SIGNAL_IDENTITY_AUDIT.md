# V4 Phase 6 — Independent Signal Identity Audit

**TEST_ID:** `SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_PHASE6_20261028T000000Z`
**Worktree:** `D:\Mirzaei\Private\1\xauusd-strategy-v4-research-20261028`
**Branch:** `research/strategy-v4-xauusd-20261028`
**Local HEAD:** `5e41fffa6a975e58d1a08fbd3510d543cd9232ba`
**Remote:** `origin/research/strategy-v4-xauusd-20261028` → `c21d41970a00ccbb7078a7bbed2fc20c14b3f163`
**Status:** read-only evidence phase; no strategy logic change, no dataset change, no existing artifact overwritten.

## 1. Scope and inputs

This audit is a standalone, offline, read-only decomposition of the existing trade artifact:

- `research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv`
- actual SHA256: `c3e5622af4aae480db7b36c8db7599ea9b91397cbb1408b0d6183da64bde3967`
- actual byte size: `1688272`
- actual data rows: `4027`

The audit script used is:

- `scripts/research/phase6_signal_identity_audit.py`
- SHA256: `3944c8e119538a66ae7dfe3c28bfac2624b77f49063c5696dede732c17f13564`
- byte size: `18315`

It does **not** import the project’s research harness, so it runs even when that harness is not importable in this worktree.

The outputs created for this phase are:

- `research/backtests/V4_PHASE6_SIGNAL_COUNTS_20261028T000000Z.csv`
- SHA256: `6138937af3cf538afb7d7364d41017bf33150485b8d1a86897444e4a35209104`
- byte size: `44123`
- data rows: `96`
- `research/manifests/V4_PHASE6_SIGNAL_AUDIT_MANIFEST.json`
- SHA256: `6356afe0b05a849b97652959f03521dfb2522d7d393faae038efb09d6de06cb3`

No existing phase-4 artifact was modified. The existing phase-4 counts CSV remains header-only and is recorded here as a prior artifact defect, not repaired in place.

## 2. Row-type and per-split counts

The source CSV contains three logically distinct row populations.

### Total row population

| Row type | Rows |
|---|---|
| `V3_RR2_TRAIL4_PROXY` | 1407 |
| `V4_TP1R_NO_TRAIL_HYPOTHESIS` | 1310 |
| Paired comparison rows (`variant` blank, `comparison_type=PAIRED_COMMON_SIGNAL`) | 1310 |
| **Total** | **4027** |

### Per-split breakdown by variant

| Variant | dataset_id | split | raw rows |
|---|---|---|---|
| V3 | development_week_2026-07-06_12 | DEVELOPMENT | 108 |
| V3 | development_month_2026-07 | DEVELOPMENT | 456 |
| V3 | validation_month_2026-08 | VALIDATION | 532 |
| V3 | fresh_holdout_available_2026-09 | FRESH_HOLDOUT_DIAGNOSTIC | 311 |
| **V3 total** | | | **1407** |
| V4 | development_week_2026-07-06_12 | DEVELOPMENT | 101 |
| V4 | development_month_2026-07 | DEVELOPMENT | 428 |
| V4 | validation_month_2026-08 | VALIDATION | 491 |
| V4 | fresh_holdout_available_2026-09 | FRESH_HOLDOUT_DIAGNOSTIC | 290 |
| **V4 total** | | | **1310** |
| PAIRED | development_week_2026-07-06_12 | DEVELOPMENT | 101 |
| PAIRED | development_month_2026-07 | DEVELOPMENT | 428 |
| PAIRED | validation_month_2026-08 | VALIDATION | 491 |
| PAIRED | fresh_holdout_available_2026-09 | FRESH_HOLDOUT_DIAGNOSTIC | 290 |
| **PAIRED total** | | | **1310** |

The PAIRED row counts are identical to the V4 row counts in every split. That is expected from the artifact structure: each paired row corresponds to a V4 variant row that has a common-matching V3 counterpart under the comparison key.

### V3-only rows by split

| dataset_id | split | V3-only rows |
|---|---|---|
| development_week_2026-07-06_12 | DEVELOPMENT | 7 |
| development_month_2026-07 | DEVELOPMENT | 28 |
| validation_month_2026-08 | VALIDATION | 41 |
| fresh_holdout_available_2026-09 | FRESH_HOLDOUT_DIAGNOSTIC | 21 |
| **Total** | | **97** |

## 3. Definitions used

### Row identity
A row is one CSV record in the existing trade artifact.

### Variant-only row
A row whose `variant` field is `V3_RR2_TRAIL4_PROXY` or `V4_TP1R_NO_TRAIL_HYPOTHESIS`.

### Paired comparison row
A row whose `variant` field is blank and whose `comparison_type` field is `PAIRED_COMMON_SIGNAL`. These are comparison records, not additional independent trades.

### Normalized key
A `frozenset`-able tuple built from selected CSV fields after trimming whitespace, with missing/empty fields treated as the empty string.

### Primary key
The key used as the main decomposition axis in this report:
`signal_timestamp + direction`

Both fields are required to be present and non-empty for a row to count as key-populated under this definition.

### Duplicate key
A normalized key that occurs more than once within one variant population, counting only rows where the key fields are populated and non-empty.

### Unmatched row
A variant-only row whose normalized key has no counterpart in the other variant under the same key definition.

### Unmatched key
A normalized key from one variant that is absent from the other variant under the same key definition.

### Paired comparison row matching
The existing artifact pairs a V4 row with a V3 row via the comparison key used by the backtest output. This audit does **not** redefine pairing. It reports how many keys exist on each side under each candidate definition and whether a source-authenticated immutable key exists.

## 4. Results for each examined key definition

The manifest attaches the same cross-variant key counts to every per-split row of a given key definition. Those counts are:

### `signal_timestamp + direction`
- V3 unique keys: 1299
- V4 unique keys: 1209
- PAIRED unique keys: 1209
- common keys: 1209
- V3-only keys: 90
- V4-only keys: 0

### `signal_time + direction + setup_index + entry_index`
- V3 unique keys: 1407
- V4 unique keys: 1310
- PAIRED unique keys: 2
- common keys: 1310
- V3-only keys: 97
- V4-only keys: 0

### `signal_time + direction + setup_index`
- V3 unique keys: 1407
- V4 unique keys: 1310
- PAIRED unique keys: 2
- common keys: 1310
- V3-only keys: 97
- V4-only keys: 0

### `signal_time + direction + entry_index`
- V3 unique keys: 1407
- V4 unique keys: 1310
- PAIRED unique keys: 2
- common keys: 1310
- V3-only keys: 97
- V4-only keys: 0

### `signal_time + direction + entry_fill_model`
- V3 unique keys: 1299
- V4 unique keys: 1209
- PAIRED unique keys: 2
- common keys: 1209
- V3-only keys: 90
- V4-only keys: 0

### `signal_time + direction + sl_anchor`
- V3 unique keys: 1299
- V4 unique keys: 1209
- PAIRED unique keys: 2
- common keys: 1209
- V3-only keys: 90
- V4-only keys: 0

### `signal_time + direction + tp_r + sl_anchor`
- V3 unique keys: 1299
- V4 unique keys: 1209
- PAIRED unique keys: 2
- common keys: 0
- V3-only keys: 1299
- V4-only keys: 1209

### `setup_index + entry_index + signal_time + direction`
- V3 unique keys: 1407
- V4 unique keys: 1310
- PAIRED unique keys: 2
- common keys: 1310
- V3-only keys: 97
- V4-only keys: 0

### Interpretation
Two families of key definitions appear:

1. Looser definitions that include `signal_timestamp` but not the paired-internal composite (`signal_time + direction + setup_index + entry_index`):  
   - common = 1209, V3-only = 90, V4-only = 0.

2. Tighter composite definitions that include both `setup_index` and `entry_index` together with the time and direction fields:  
   - common = 1310, V3-only = 97, V4-only = 0.

One apparently plausible stricter key, `signal_time + direction + tp_r + sl_anchor`, does **not** behave like the others: under it, common = 0, V3-only = 1299, V4-only = 1209. So a “cleaner” match count is not a property of the data by itself; it depends on which fields are treated as part of the identity.

## 5. Are `setup_index`, `entry_index`, and related fields source-authenticated identifiers?

No.

The trade CSV contains fields such as `setup_index`, `entry_index`, `source_rule_id`, `ticket`, `order_id`, `position_id`, and `deal_id`. Some of those are visually “ID-like”, but that does not make them independent source-authenticated signal identities for this audit.

In this artifact:

- `setup_index` is populated on variant-only rows, but it is **blank** on paired comparison rows.
- `entry_index` is populated on variant-only rows, but it is also **blank** on paired comparison rows.
- The paired comparison rows therefore do **not** carry the same internal bookkeeping identifiers as the variant-only rows.
- The only fields populated on the paired rows are the comparison-oriented fields: `signal_timestamp`, `direction`, `comparison_type`, `baseline_exit`, `v4_exit`, `baseline_gross_R`, `v4_gross_R`, `delta_gross_R`, and `status`.

So even if `setup_index` or `entry_index` were treated as locally unique within the variant-only population, they are not available as a consistent identity key across the paired comparison population. The comparison was built on a different identity notion than the variant-level bookkeeping.

Also:

- `source_rule_id` is not an immutable signal identity. It is a research-labeling field; in this artifact it is constant within each variant rather than distinguishing signals.
- `ticket`, `order_id`, `position_id`, and `deal_id` are present in the CSV schema, but they are not reliable trade-level identity handles in this artifact because they are not populated consistently across the populations that matter for the comparison.

Therefore, the available fields do not provide a single source-supported immutable signal identity that:

- exists on every relevant row,
- is defined by the original strategy source rather than the backtest output tooling,
- and yields the same identity conclusion regardless of which admissible fields are included.

## 6. Reconciliation of 90 V3-only keys versus 97 V3-only rows

The two numbers answer different questions.

- **90 V3-only keys** is the distinct-key count under the looser primary definition `signal_timestamp + direction`.
- **97 V3-only rows** is the row-level count of V3 variant-only rows whose primary key is absent from V4.

These differ because some unmatched keys occur more than once on the V3 side. In this artifact, V3-only keys total 90 distinct values across 97 rows, which means 7 extra rows sit under keys that already appeared at least once among the V3-only set.

The split distribution of V3-only rows by dataset/split is:

- development_week_2026-07-06_12 / DEVELOPMENT: 7
- development_month_2026-07 / DEVELOPMENT: 28
- validation_month_2026-08 / VALIDATION: 41
- fresh_holdout_available_2026-09 / FRESH_HOLDOUT_DIAGNOSTIC: 21

So the difference between 90 and 97 is not a counting mistake. It is the difference between “distinct unmatched signals” and “unmatched variant rows”, and the report keeps them separate.

Under the tighter composite keys that include both `setup_index` and `entry_index`, the V3-only count rises to 97 distinct keys, which matches the 97 V3-only rows. That is consistent with those keys being more discriminating on the V3 side than the looser timestamp+direction definition.

## 7. Limitations of the paired records

The paired rows have their own limitations and must not be treated as independent trades.

- They are comparison records (`variant` blank, `comparison_type=PAIRED_COMMON_SIGNAL`).
- In this artifact they do not carry filled baseline or V4 entry identifiers; the variant-only rows do.
- Their `status` field is not mixed with the variant-only rows’ status field.
- Across all 1310 paired rows:
  - `PASS` = 42
  - `UNRESOLVED` = 1268
- Their `baseline_exit` distribution:
  - `AMBIGUOUS_SAME_BAR_PATH` = 1267
  - `ORIG_SL` = 43
- Their `v4_exit` distribution:
  - `TP` = 803
  - `ORIG_SL` = 480
  - `AMBIGUOUS_SAME_BAR_PATH` = 14
  - `CENSORED_DATA_GAP_OR_WINDOW` = 13

So the paired set is overwhelmingly unresolved on the baseline-comparison side, with a small PASS subset and a materially different exit profile between the two variants. The paired set therefore cannot be used as a neutral paired inference sample without first resolving why the baseline side is almost entirely ambiguous in this artifact.

## 8. Source-supported immutable signal identity

Not established.

The existing artifact does not contain a field that is simultaneously:

- populated on both variant-only and paired rows,
- defined by the original strategy source rather than the backtest tooling,
- and invariant to which admissible fields are included in the key.

The two main candidate families each fail a different part of that bar:

- The timed-based definitions that match the paired population are not source-authenticated as the strategy’s immutable signal identity; they are the artifact’s comparison key.
- The tighter variant-level bookkeeping fields do not exist on the paired rows.

So the audit cannot confirm that “common key” means “same underlying strategy signal” in a source-authenticated sense.

## 9. Final verdict

**SIGNAL_IDENTITY_NOT_ESTABLISHED**

The phase-6 evidence shows:

- V4 has no V4-only keys relative to V3 under any of the examined definitions.
- V3 has unmatched keys under every examined definition:
  - 90 distinct V3-only keys under `signal_timestamp + direction`
  - 97 distinct V3-only keys under the tighter `signal_time + direction + setup_index + entry_index` family
- The 90-vs-97 difference is a real row-vs-key distinction, not a reconciliation error.
- The matched counts change with the chosen key definition, including a definition where common = 0.
- No source-supported immutable signal identity exists in the existing artifact.
- The paired rows are comparison records, not independent trades, and are mostly UNRESOLVED on the baseline side.

Therefore, the paired comparison is **not** validated here as a clean paired identity, and the strategy status remains **BLOCKED / NOT_PROVEN**.

## 10. Actual commands and exit codes

First run:
- `python scripts/research/phase6_signal_identity_audit.py --trades-csv research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv --output-csv research/backtests/V4_PHASE6_SIGNAL_COUNTS_20261028T000000Z.csv --manifest research/manifests/V4_PHASE6_SIGNAL_AUDIT_MANIFEST.json`
- exit code: 0

Deterministic rerun:
- same command, second invocation
- exit code: 0
- stdout payload identical to first run: True
- manifest `deterministic_rerun_verified`: True

Validation embedded in the run:
- variant V3 rows expected 1407, actual 1407, match True
- variant V4 rows expected 1310, actual 1310, match True
- variant PAIRED rows expected 1310, actual 1310, match True
- total rows expected 4027, actual 4027, match True

### Artifact hashes

| Artifact | SHA256 | bytes |
|---|---|---|
| `scripts/research/phase6_signal_identity_audit.py` | `3944c8e119538a66ae7dfe3c28bfac2624b77f49063c5696dede732c17f13564` | 18315 |
| `research/backtests/V4_PHASE6_SIGNAL_COUNTS_20261028T000000Z.csv` | `6138937af3cf538afb7d7364d41017bf33150485b8d1a86897444e4a35209104` | 44123 |
| `research/manifests/V4_PHASE6_SIGNAL_AUDIT_MANIFEST.json` | `6356afe0b05a849b97652959f03521dfb2522d7d393faae038efb09d6de06cb3` | 2340 |

### Protected files unchanged

All protected files matched their pre-phase hashes exactly:

- `research/backtests/SP2L_XAUUSD_STRATEGY_V4_RESEARCH_20261028T120000Z_trades.csv`: unchanged
- `scripts/research/phase4_signal_identity_audit.py`: unchanged
- `research/validation/V4_PHASE4_GIT_TREE_AUDIT.md`: unchanged
- `research/validation/V4_PHASE4_SIGNAL_IDENTITY_AUDIT.md`: unchanged
- `research/backtests/V4_PHASE4_SIGNAL_COUNTS_20261028T000000Z.csv`: unchanged
- `research/manifests/V4_PHASE4_AUDIT_MANIFEST.json`: unchanged
- `research/engine/test_acquire_xauusd.py`: unchanged
- `tests/test_discover_mt5_research_symbols.py`: unchanged
- `tests/test_sp2l_mt5_data_quality_gate.py`: unchanged

### Reproduction outputs retained
- `research/runtime_audit/phase6_run1.json`
- `research/runtime_audit/phase6_run2.json`
- `research/runtime_audit/phase6_run_final.json`

## 11. Unresolved items

1. No source-authenticated immutable signal identity was established.
2. The existing paired comparison is definition-dependent and not independently authenticated.
3. The existing phase-4 counts CSV is header-only; it was not overwritten and remains a defect.
4. The existing phase-4 signal-identity report is truncated; it was not repaired here.
5. Remote-only `research/validation/V4_TRADE_ARTIFACT_SEMANTICS_AUDIT.md` still exists only on the remote branch; it was not restored locally.
6. Strategy status remains `BLOCKED / NOT_PROVEN`.

## 12. Exact worktree status at completion

- branch: `research/strategy-v4-xauusd-20261028`
- HEAD: `5e41fffa6a975e58d1a08fbd3510d543cd9232ba`
- remote-tracking: `origin/research/strategy-v4-xauusd-20261028` → `c21d41970a00ccbb7078a7bbed2fc20c14b3f163`
- modified: `research/engine/test_acquire_xauusd.py`, `tests/test_discover_mt5_research_symbols.py`, `tests/test_sp2l_mt5_data_quality_gate.py`
- new untracked phase-6 artifacts:
  - `scripts/research/phase6_signal_identity_audit.py`
  - `research/backtests/V4_PHASE6_SIGNAL_COUNTS_20261028T000000Z.csv`
  - `research/manifests/V4_PHASE6_SIGNAL_AUDIT_MANIFEST.json`
  - `research/runtime_audit/phase6_run1.json`
  - `research/runtime_audit/phase6_run2.json`
  - `research/runtime_audit/phase6_run_final.json`
- nothing staged, nothing committed, nothing pushed.
