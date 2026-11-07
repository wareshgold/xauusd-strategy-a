# Weekly Audit Report Template

> Status: NOT YET POPULATED — no conclusions may be drawn from this template.

## 1. Run identity
- Capture timestamp / timezone:
- Runner process count and process IDs:
- Executable path:
- Command line:
- Config/version fingerprint:
- Git branch and commit:
- Symbol / magic:
- Identity match: PASS / FAIL / INDETERMINATE

## 2. Evidence integrity
| Artifact | Time coverage | Bytes/rows | SHA-256 | Completeness |
|---|---:|---:|---|---|
| Runner events | | | | |
| State snapshots | | | | |
| MT5 orders | | | | |
| MT5 deals | | | | |
| M1 bars | | | | |
| Tick data | | | | |

## 3. Population and reconciliation
- Pending orders in scope:
- Filled positions:
- Closed positions:
- Open positions at cutoff:
- Unmatched runner events:
- Unmatched MT5 orders/deals:
- Duplicate or conflicting records:

## 4. Realized performance
| Metric | Value | Method / caveat |
|---|---:|---|
| Closed positions | | |
| Gross P/L | | |
| Commission | | |
| Swap | | |
| Fees | | |
| Net P/L | | |
| Win rate | | |
| Profit factor | | |
| Maximum drawdown | | |

## 5. Per-position diagnostics
Include a private evidence-linked table with entry/exit timestamps, direction, actual fill, gross/net P&L, MFE, MAE, holding time, pending lifecycle, SL/TP timeline, and reconciliation status. Do not publish identifying raw fields in this public repository.

## 6. Trailing audit
- Eligible activation events:
- Successful SL modifications:
- Rejected modifications (retcode and reason):
- Deferred/retried modifications:
- Cases where history was unavailable:
- Verified implementation behavior vs source:
- Unresolved behavior:

## 7. Counterfactuals
Use identical actual fills and explicitly defined exit assumptions. Report assumptions, excluded cases, costs, sample size, and uncertainty. No inferred entry or fill rules.

## 8. Limitations
Document tick/M1 coverage, intrabar ambiguity, clock offset uncertainty, broker history gaps, source-to-process identity gaps, and unresolved source semantics.

## 9. Finding and next research gate
- Finding:
- Evidence supporting it:
- Evidence against it:
- Confidence:
- Next research task:
- Explicitly prohibited live changes:
