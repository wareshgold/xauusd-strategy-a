# SP2L V3.1 Weekly Forensic Audit
## Window
2026-11-02 00:00:00 through 2026-11-07 23:59:59 (runner/server time must be established from evidence).

## Safety and scope
- This repository is public. Do not commit raw MT5 account history, account/login identifiers, order/deal/position tickets, exact trade timestamps, exact prices, terminal paths, credentials, or unredacted runner logs.
- This branch contains audit methodology and templates only. Raw evidence must remain in private storage until an explicitly approved private transfer path is available.
- No runner, MT5 terminal, orders, positions, configuration, or live process may be changed for this audit.
- This is a diagnostic weekly sample, not an untouched holdout or proof of out-of-sample edge.
- No production BUY/SELL decisions are produced.

## Audit questions
1. What is the complete in-scope population of entries, pending orders, fills, positions, and exits for the audit window?
2. What is realized net P/L after commission, swap, and fees, reconciled to MT5 deals?
3. Are event records, order/deal history, position history, and state snapshots internally consistent?
4. Did pending-order expiry, cancellation, replacement, or fill behavior contribute to losses?
5. What do MFE/MAE and exit timing show for each filled position?
6. Did trailing activation and SL modifications occur according to the observed implementation? Separate successful modifications, rejected modifications, deferred attempts, and unavailable history.
7. What can be tested counterfactually using the same actual fills without changing entry generation?
8. Which conclusions are blocked by missing tick data, M1 intrabar ambiguity, history-query failures, or unresolved source semantics?

## Required evidence (retain raw originals privately)
- Runner process identity, executable path, command line, version/config fingerprint, branch/commit, and capture time.
- Event JSONL covering the full window, plus SHA-256.
- State snapshots and their SHA-256 values.
- MT5 order/deal/position history for the full window, including commission, swap, fee, and reason fields where available.
- Symbol specification and broker/server time offset evidence.
- M1 bars and tick data spanning each position from entry through exit, with provenance and hashes.
- Relevant runner source files at the exact running commit; source files are not proof of the running process unless identity is independently matched.

## Required analysis
- Reconcile all in-scope MT5 deals to positions and runner events; report unmatched records rather than silently dropping them.
- Calculate realized gross and net results, with costs itemized.
- Calculate MFE/MAE from available tick data where possible. Label M1-derived estimates as approximate and disclose intrabar ambiguity.
- Build a per-position timeline: signal/entry candidate, pending placement, fill, SL/TP changes, exit, and deal accounting.
- Evaluate management counterfactuals only on the same observed fills. Do not change entry population or invent fill semantics.
- Treat any P-Gap, AB=CD anchor/tolerance, SL-anchor meaning, or fill/execution semantics not explicitly source-confirmed as unresolved.
- Report sample size, missingness, uncertainty, and sensitivity. Do not promote weekly results to canonical rules.

## Decision gate
A recommendation to continue research, pause for data repair, or investigate execution must cite the reconciled population and quantify uncertainty. No live configuration change is authorized by this audit.

## Evidence transfer
Because this repository is public, upload only reviewed, disclosure-safe aggregate outputs here. Keep raw evidence in private storage. Do not add raw evidence to this branch.
