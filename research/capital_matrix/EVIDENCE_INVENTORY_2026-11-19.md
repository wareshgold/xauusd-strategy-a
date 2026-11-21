# Evidence Inventory — SP2L Capital Management Study

**Audit date:** 2026-11-19  
**Purpose:** Read-only source inventory following the official project snapshot.  
**Research branch:** `research/capital-management-matrix-20261119`  
**PR:** #422 (open, draft, not merged).  
**Current branch head verified from PR:** `ea3103661494ff9dba44ef822670ed55ad0706ff`.

## 1. Current branch verification

The following files were fetched directly from the research branch:
- `research/capital_matrix/matrix.py`
- `research/capital_matrix/README.md`
- `tests/research/test_capital_matrix.py`
- `.github/workflows/research-capital-matrix.yml`
- `research/capital_matrix/PROJECT_SNAPSHOT_2026-11-19.md`

The matrix source enumerates 89 unique configurations and implements the initial risk-budget/volume-sizing primitives. The test file contains eight unit tests. The user ran the tests locally and supplied the output `Ran 8 tests ... OK`, `TEST_EXIT_CODE=0`. The workflow exists, but this inventory does not claim a GitHub Actions run passed.

## 2. Earlier three-month acquisition and population workflow found

A separate pre-existing branch was found:
- Branch: `research/three-month-management-matrix-20261109`
- Branch commit inspected: `ad8dcf9fbad4f3e83bdb4504ec0bea0097e32a67`

Its documentation and scripts include:
- `docs/SP2L_THREE_MONTH_MT5_EXPORT.md`
- `docs/SP2L_V31_THREE_MONTH_ENTRY_POPULATION.md`
- `scripts/acquire_sp2l_three_month_mt5_data.py`
- `scripts/build_sp2l_v3_1_frozen_population_from_m1.py`

The acquisition instructions describe a read-only MT5 export utility for Tick ALL and M1. It writes gzip CSVs, symbol specifications, a manifest and SHA sums; it does not send orders or modify positions. This is documentation of a user-operated acquisition workflow, not evidence that the output files are presently available.

## 3. Declared three-month M1 source identity

The entry-population document declares the expected M1 CSV.GZ SHA-256:

`daf4eb26c47ef0dadc045c76b9a72b667751e1eac315697a6b024e81e355c402`

It documents:
- 89,866 M1 bars.
- First bar: `2026-08-10T01:00:00Z`.
- Last bar: `2026-11-09T07:43:00Z`.
- 66 timestamp gaps.
- The file does not represent complete continuous coverage of the requested interval.

These are values declared in the repository's acquisition/population documentation. The raw gzip file was not available in the inspected GitHub tree or returned by the Library searches in this audit, so its bytes and SHA-256 have **not** been independently re-verified in this step.

The entry builder's documented acceptance requirements are: source SHA must match exactly; source row count and first/last UTC must match; output CSV and manifest hashes must be retained; all management variants must share the same population SHA; monthly/directional entry counts must be recorded; gaps must remain visible.

## 4. Other historical files are not substitutes

The GitHub tree contains older monthly acquisition manifests and a shorter M1 CSV. For example, the August manifest records 28,957 returned bars against 28,980 expected and marks the audit `AUDITED_FAIL`; its historical session-calendar applicability is `UNVERIFIED`. The September manifest records 17,069 returned bars against 17,940 expected and also leaves historical session-calendar applicability unverified.

A prior local inventory also listed:
- A 30-day M1 CSV at `D:\Mirzaei\Private\1\sp2l-mt5-market-data\20261024T075827Z\xauusd_ecn_m1_30d.csv` (29,919 rows, 2026-09-24 to 2026-10-23).
- Separate August, September and partial-October monthly files.
- The 462-row frozen V3 entry population belongs to the 30-day Discovery window, not the three-month population.

Do not concatenate these older files, relabel the 30-day population as three months, or substitute any of them for the declared SHA-pinned three-month source.

## 5. Tick and broker evidence

The earlier exporter is designed to produce Tick ALL Bid/Ask data and current symbol specifications. The inspected GitHub tree contains the exporter and tick-audit code, but no matching three-month raw Tick ALL gzip corpus or acquisition manifest for the required population was identified in this audit.

Current symbol specifications are not automatically historical specifications. Before sizing or cost calibration, preserve the exact account/symbol contract fields, commission convention, swap, spread and execution assumptions alongside the dataset. Do not infer these from synthetic unit-test fixtures.

## 6. Audit conclusion

**Historical replay readiness: BLOCKED pending local evidence verification.**

No historical simulation or performance ranking should begin until the operator locates the exact M1 CSV.GZ and its acquisition manifest/SHA sums, the generated three-month entry CSV and manifest, Tick ALL data (or an explicitly approved lower-evidence OHLC policy), and broker cost/contract metadata.

## 7. Next action

Perform a read-only search on the Factory PC for files matching the declared M1 SHA-256 and the three-month entry-population manifest. Hash candidate files before use. If the exact source cannot be found, stop and plan a new evidence acquisition under the documented read-only exporter; do not connect to MT5 from this research workflow or reuse/overwrite old evidence.

No Runner, dashboard, MT5 terminal, account state, order or production configuration was accessed or changed by this inventory.
