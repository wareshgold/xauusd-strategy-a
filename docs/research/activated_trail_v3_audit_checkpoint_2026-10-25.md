# Strategy A Activated-Trailing Proxy V3 — Audit Checkpoint (2026-10-25)

## Scope

This checkpoint records the read-only local discovery evidence supplied for the monthly OHLC activated-sensitivity audit. It does not certify the proxy as source-faithful, change Strategy A geometry, or authorize production use.

## Artifact identity

Two paths were reported:

1. `artifacts/monthly_ohlc_activated_sensitivity_v3_20261024_162634_105/a_trail_0_40_activated_proxy_v3_trades.csv`
2. `artifacts/research_snapshot_activated_trail_v3_20261025_083252_543/proxy_output/a_trail_0_40_activated_proxy_v3_trades.csv`

Both reported:
- Size: 84,818 bytes
- Data rows: 462
- Columns: `strategy, variant, direction, setup_time_utc, entry_time_utc, entry_proxy, sl_initial, target, risk_price, exit_time_utc, exit_price, exit_reason, status, r_multiple`
- Variant: `A_TRAIL_0_40_ACTIVATED_PROXY_V3`
- Last write: `2026-10-24T16:26:36.0093738+03:30`
- SHA-256: `39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1`

The snapshot manifest's `proxy_output/a_trail_0_40_activated_proxy_v3_trades.csv` entry reports the same byte count and SHA-256. This establishes consistency among the reported hashes and manifest entry; it is not an independent byte-for-byte comparison because the underlying files are not attached to this GitHub change.

## First-row diagnostic flag

The first reported row is:
- Direction: BUY
- Setup: `2026-09-24T08:47:00Z`
- Entry time: `2026-09-24T08:48:00Z`
- Entry proxy: 4284.00
- Initial SL: 4280.04
- Target: 4291.92
- Risk price: approximately 3.96
- Exit time: `2026-09-24T08:50:00Z`
- Exit price: approximately 4284.12
- Exit reason: `SL`
- Status: `CLOSED`
- R multiple: `+0.03030303`

The reported exit is above entry while the exit reason is `SL`. This is a diagnostic flag, not proof of a defect: a moved stop could potentially explain it, but the CSV excerpt alone does not prove that a trailing stop was activated or that intrabar event ordering was modeled correctly.

## Evidence status

### Confirmed from supplied discovery output
- Both CSV reports have the same reported SHA-256, byte size, row count, columns, variant, and modification time.
- The manifest entry matches the reported CSV hash and size.
- The sample row has an `SL` exit reason and a positive R multiple.

### Not yet established
- Independent byte-for-byte equality of the two on-disk files.
- Correctness of every row's R multiple and exit classification.
- Trailing activation conditions and stop-update timing.
- OHLC intrabar ordering / stop-versus-target precedence.
- Whether the proxy semantics match a source-confirmed Strategy A rule.
- Any statistically validated edge or production readiness.

## Next audit steps (read-only first)

1. Recompute SHA-256 and compare the two files byte-for-byte in the local worktree; preserve all existing artifacts.
2. Independently recompute `r_multiple` from each row's entry, initial risk, direction, and exit price, while explicitly checking for any documented alternative convention.
3. Tabulate `exit_reason` against signed exit movement and R multiple; inspect all `SL` exits with positive R and all other inconsistent combinations.
4. Trace the proxy implementation and its tests for activation, stop movement, OHLC event ordering, and tie/ambiguous-bar handling.
5. Keep any unresolved behavior labeled diagnostic/unresolved until source evidence settles it. Do not infer or canonize a P-Gap formula, AB=CD anchors/tolerance, fill semantics, or execution rules from performance.

## Guardrails

- Research-only; no production BUY/SELL authority.
- No strategy geometry or execution semantics are changed by this checkpoint.
- No historical results are reclassified without traceable evidence.
- Preserve source artifacts and snapshots; no cleanup/reset or overwrite.
- Fresh holdout remains required after rules and geometry are frozen.


## GitHub repository inspection update

The GitHub repository tree was inspected directly on branch `research/monthly-matrix-ohlc-proxy-20261024` (tree SHA `c858d9aae97a0e0c1c0d0c4ca15911cf732e7b42`). The two exact generated trade CSV paths listed above are **not tracked in that branch's Git tree**. Searches for the exact filename, snapshot directory, and supplied SHA-256 also returned no indexed code/file match. Therefore the local CSV output cannot be independently read from GitHub at those exact paths; the supplied local report remains the evidence for its row-level identity.

Relevant implementation files do exist on GitHub:
- `scripts/research/monthly_matrix_ohlc_proxy_backtest.py`
- `scripts/research/monthly_matrix_source_audit.py`
- `scripts/research/monthly_matrix_trail_same_bar_ambiguity_diagnostic.py`

The proxy implementation explicitly labels itself hypothetical/non-canonical and states these assumptions: theoretical trigger price as entry proxy; exit checks start after the trigger bar; same-bar stop and target both touched means stop-first; gap-through exits use the next observed bar's open; trailing distance is 0.40 price units from the best completed-bar high/low, with updates effective on the next bar. These are implementation assumptions, not source-confirmed execution semantics. The code's declared expected input SHA-256 is `b0782e716c7eccbd29ef25e146c088b356f2aadf2ccd5d7ea24e6ac1488aa285`; that input hash must be reconciled with the actual frozen monthly OHLC file before any rerun or result is trusted.

A different branch, `research/rr2-trail4-vs-pythontraderbot-monthly-matrix-20261024`, contains other historical CSV/JSON research artifacts (including multi-megabyte exit matrices and M1 acquisition files), but those are not the exact 462-row activated-proxy output and must not be substituted for it.

## Diagnostic-tool correction

The first local run displayed one blank `exit_price` at CSV line 463. The original diagnostic incorrectly treated every non-numeric row as an invalid numeric row even when the trade status is unresolved and exit fields are expected to be blank. The audit script has now been updated to:
- perform R arithmetic only on rows whose status is `CLOSED`;
- count and report non-closed/unresolved rows separately;
- flag partially populated exit fields on unresolved rows without treating ordinary blank exits as malformed;
- retain the byte-for-byte comparison and positive-R `SL` diagnostics.

This correction is committed on the audit branch. The corrected script has been fetched back from GitHub, but still needs to be rerun against the actual local CSVs before drawing row-level conclusions.
