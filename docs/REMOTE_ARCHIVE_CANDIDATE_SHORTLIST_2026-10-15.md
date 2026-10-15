# Remote Archive Candidate Shortlist — 2026-10-15

**This is a review queue, not a deletion list. No remote refs were deleted or modified.**

## Method and limits

- Compared the current paginated remote branch list (329 refs) with closed/merged PR metadata (48 merged PRs returned) and open PR metadata (54 open PRs returned).
- A branch enters this shortlist only if its current remote HEAD exactly matches the latest merged PR head SHA for that branch, and its branch name is not currently used as an open PR head or base.
- This is a necessary signal, not sufficient proof of safe deletion. The API's branch list and PR snapshot can race with new commits/PRs.
- Before deletion, inspect branch ancestry against its actual target, dependent branches, unique artifacts, and local clones/worktrees. Keep a verified recovery SHA/tag.
- This shortlist says nothing about Windows local-only branches or dirty/untracked files.

- Exact-head matches eligible for further review: **42**
- Current authorization to delete: **none**.

## Candidate rows

| Branch | Current HEAD SHA | Merged PR(s) | Latest merged PR / base | Proposed status |
|---|---|---|---|---|
| `diagnostics/forward-runner-silent-poll-20261015` | `ad78769983b9a12f2d5d98018959572f115036b4` | #326 | #326 — Add rate-limited diagnostics for silent V3 forward polling (base `fix/rr2-trail4-pending-clock-offset-20261015`) | REVIEW_REQUIRED |
| `feat/factory-raw-m1-audit-candidate-lab-20261015` | `247c0d7a727fdfcfe34368b12ae3b49bfbe1ed5a` | #320 | #320 — feat(factory): integrate raw M1 audit into candidate lab (base `research/factory-candidate-lab-20261010`) | REVIEW_REQUIRED |
| `feat/factory-raw-m1-integrity-audit-20261015` | `4f3191e4471b803fbcbe448de3add3b54d250df7` | #318 | #318 — feat(factory): add read-only raw M1 CSV integrity audit (base `research/xauusd-availability-integrity-gate-20261013`) | REVIEW_REQUIRED |
| `feature/factory-external-strategy-comparison-20261008` | `040583f61f3f0f261eb5edf31a78c014cb642ac2` | #286 | #286 — research(factory): add external SP2L 1v1 comparison boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `fix/dashboard-open-closed-trades-20261008` | `749e41ef1c3b483887d3a0309bcbe6d7e01e146a` | #268 | #268 — feat: show open and closed MT5 trades in dashboard (base `research/sp2l-v3-forward-reconciliation-20261003`) | REVIEW_REQUIRED |
| `fix/factory-empty-availability-windows-20261015` | `9ec2310276c014db2fce9decd07aa252aa1f2bae` | #317 | #317 — fix(factory): reject empty availability window manifests (base `research/xauusd-availability-integrity-gate-20261013`) | REVIEW_REQUIRED |
| `fix/factory-raw-m1-audit-local-regressions-20261015` | `7b8b02c64eacb54ae7fa53d4e29bd232a9741d51` | #319 | #319 — fix(factory): resolve raw M1 audit local regressions (base `feat/factory-raw-m1-integrity-audit-20261015`) | REVIEW_REQUIRED |
| `fix/factory-raw-m1-line-ending-hash-20261015` | `a186cf7c888095ae1b4c54bb582c0d7088c1a089` | #322 | #322 — Fix raw M1 audit for Windows CRLF checkouts (base `research/factory-candidate-lab-20261010`) | REVIEW_REQUIRED |
| `fix/factory-tick-acquisition-no-overwrite-20261014` | `44acabeba7a0cf5465046924e5b716553cd5ede5` | #308 | #308 — Prevent Factory tick acquisition from overwriting evidence (base `research/xauusd-availability-integrity-gate-20261013`) | REVIEW_REQUIRED |
| `fix/factory-timestamp-audit-empty-csv-20261015` | `54fa07fe43033f8756987c5e6021c0d3b09faf09` | #316 | #316 — fix(factory): fail timestamp audit on empty CSV (base `research/xauusd-availability-integrity-gate-20261013`) | REVIEW_REQUIRED |
| `fix/full-suite-baseline-regressions-20261014` | `7e79cae35e2c59b719df0ba765a00af14ae78b0d` | #304 | #304 — Fix five baseline test-suite regressions (base `fix/rr2-trail4-deal-history-position-query-20261014`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-all-blocked-notifications-20261013` | `ab5a7400967d7206305e06d7da711b9b3910f23c` | #292 | #292 — Notify Telegram when volume guard blocks a forward signal (base `fix/rr2-trail4-pending-lifecycle-safe-20261011`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-deal-history-position-query-20261014` | `41aa1f459aeb3a5b823349894583864fc1a16ac6` | #303, #310 | #310 — Forward-port verified RR2/TRAIL4 lifecycle guards (base `fix/rr2-trail4-telegram-deal-time-20261013`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-deal-lifecycle-server-time` | `6311c949b561105e278a18209da47e15f4cab468` | #266, #267 | #267 — fix: restore RR2/TRAIL4 deal lifecycle reconciliation (base `research/sp2l-rr2-trail4-daily-replay-20261008`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-history-guards-preserve-pip-display-20261014` | `6b23005ef5dbfe05af257ae24ad53ea495c4190a` | #311 | #311 — Preserve RR2/TRAIL4 pip display with lifecycle history guards (base `fix/rr2-trail4-telegram-deal-time-20261013`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-history-query-log-dedup-20261015` | `e4f3c3e476a4ed83c5bc6748441ced4e765e8274` | #313 | #313 — Deduplicate repeated RR2/TRAIL4 MT5 history failure events (base `fix/rr2-trail4-telegram-deal-time-20261013`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-history-query-position-only-20261015` | `31ef5590c2d4e4d25642bd93a00714d1f1bafd97` | #324 | #324 — Fix RR2/TRAIL4 deal-history query semantics (base `fix/rr2-trail4-pending-clock-offset-20261015`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-lifecycle-query-fail-guard-20261014` | `3957176d795115949d63617e39bff9c4fbc78893` | #309 | #309 — Guard RR2/TRAIL4 lifecycle history failures and stale deals (base `fix/rr2-trail4-deal-history-position-query-20261014`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-lifecycle-reconciliation-guards-20261013` | `fb4f479f9d158f8e0baeee126f51be9e74efda34` | #301 | #301 — Guard RR2/TRAIL4 lifecycle reconciliation against MT5 query failures (base `fix/rr2-trail4-pending-lifecycle-safe-20261011`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-safe-newlines-20261013` | `9fe921101f13ce77e22f370c0a6149b822f61b10` | #291 | #291 — Fix literal newlines in blocked-order Telegram alerts (base `fix/rr2-trail4-pending-lifecycle-safe-20261011`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-position-reconciliation-gap-20261013` | `8100e2444f9b33f61b39edf73b82b4340fa73f14` | #300 | #300 — Add explicit RR2/TRAIL4 position reconciliation diagnostics (base `fix/rr2-trail4-pending-lifecycle-safe-20261011`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-telegram-newlines-20261013` | `8a3ad94ab61c974b3fd783d83f0f2ece0fefc565` | #290 | #290 — Fix literal newlines in blocked-order Telegram alerts (base `fix/rr2-trail4-telegram-deal-time-20261013`) | REVIEW_REQUIRED |
| `fix/rr2-trail4-v3-dashboard-data-20261015` | `210016d1ebc8f74b7e99f7544ca5c3f481838366` | #325 | #325 — Fix RR2/TRAIL4 dashboard V3 data sources and progress diagnostics (base `fix/rr2-trail4-pending-clock-offset-20261015`) | REVIEW_REQUIRED |
| `hardening/forward-reconciliation-provenance-20261008` | `8a2f49fc100f6f0fa5df841bf9ae7a833c627018` | #273 | #273 — test(factory): preserve handoff provenance through reconciliation (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `hardening/forward-session-lifecycle-identity-20261008` | `02a76a2fae97b524a2a88a3ce9a59c1f02df5166` | #272 | #272 — test(factory): freeze Forward session lifecycle identity (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `hardening/holdout-forward-provenance-20261008` | `b4be909fa2091c4093b8ad1bddbb94fab0059e1e` | #271 | #271 — test(factory): preserve Holdout handoff provenance into Forward session (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `research/factory-timestamp-sequence-audit-20261014` | `b8c6644be6ff45deaf84fb9a3fe4714cdbc2d157` | #312 | #312 — Factory: add read-only timestamp sequence audit (base `research/xauusd-availability-integrity-gate-20261013`) | REVIEW_REQUIRED |
| `research/raw-m1-synthetic-fixtures-20261015` | `b344534a7e6de63bfd3b32a564e89beab19ec218` | #321 | #321 — test(factory): expand raw M1 synthetic integrity fixtures (base `research/factory-candidate-lab-20261010`) | REVIEW_REQUIRED |
| `research/rr2-trail4-telegram-checkpoint-20261013` | `c3fe369c613fcaf43dd3a3e1b21e3e3b06fb989c` | #294 | #294 — Checkpoint RR2/TRAIL4 Telegram forward evidence (base `fix/rr2-trail4-telegram-deal-time-20261013`) | REVIEW_REQUIRED |
| `research/rr2-trail4-trailing-matrix-20261013` | `a58c67614b341ab68aa2eb64d02a25d66750aa46` | #295 | #295 — Add independent RR2/TRAIL4 trailing backtest matrix (base `fix/rr2-trail4-telegram-deal-time-20261013`) | REVIEW_REQUIRED |
| `research/sp2l-forward-observed-evidence-20261008` | `f9a055496c46842fc6ded0893d6db78ffa86e1e4` | #281 | #281 — feat(factory): add immutable forward observed evidence contract (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `research/sp2l-forward-observed-report-20261008` | `1fc44fd2152ce414a705324372cf75058ad997e2` | #282 | #282 — feat(factory): add deterministic forward observed report (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `research/sp2l-r-mapping-source-gate-20261008` | `b61e11137aab9d82f89ed67f0d8392c4b86b8e0f` | #283 | #283 — research(factory): freeze R trade-return source boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `snapshot/sp2l-rr2-trail4-dashboard-20261008` | `6ee250a4b192bcb4f16eb8dfe8ad1bb1d221e170` | #269 | #269 — docs: snapshot RR2 TRAIL4 dashboard forward state (base `research/sp2l-v3-forward-reconciliation-20261003`) | REVIEW_REQUIRED |
| `test/factory-forward-runtime-fail-closed-20261008` | `84c4f6f4da922ca8ef891aca82712a308a9c513a` | #280 | #280 — test(factory): harden forward runtime fail-closed boundaries (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-fresh-holdout-forward-boundary-20261008` | `b98945368b71c587bdf529dff54b7ac53b3e8800` | #279 | #279 — test(factory): prove fresh holdout to forward boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-full-provenance-e2e-20261008` | `3db15d000c9199794d7e9001ddd0882a4f0999dc` | #274 | #274 — test(factory): prove full holdout-to-reconciliation provenance (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-holdout-forward-e2e-20261008` | `1c7a85c9f3e86956cac4ce0048fdb8e8c48f0b28` | #270 | #270 — test(factory): cover Fresh Holdout to Forward E2E boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-provenance-negative-hardening-20261008` | `4d5756458a62f9bd274a7181def83cf54650b085` | #275 | #275 — test(factory): harden provenance drift rejection (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-robustness-holdout-boundary-20261008` | `37df87d13a641832c089e942f2ee6f20775040b0` | #278 | #278 — test(factory): harden robustness to fresh holdout boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-untouched-validation-boundary-20261008` | `2e661bcf790920dcadfe005d282ea6ec1dfe4743` | #276 | #276 — test(factory): prove untouched validation boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |
| `test/factory-validation-robustness-boundary-20261008` | `7173ef08ef90c8ef4f262bdb83ca8d2771cc47f7` | #277 | #277 — test(factory): harden validation to robustness boundary (base `research/sp2l-starnet-engine-integration-20261007`) | REVIEW_REQUIRED |

## Review batches

### Forward Test

Prioritize lifecycle and dashboard fix branches only after checking whether their unique commits are included in the approved current Forward reference. A merged PR does not prove the branch head is contained in the desired runtime base, especially where PR bases are nested or divergent.

### Factory

Prioritize completed raw-M1 audit and timestamp-integrity fix branches after confirming their work is included in the chosen Factory integration head. Do not archive the Factory integration branch or open PR heads/bases.

### Backtest / Source Research

Preserve research reports, fixtures, dataset manifests, and forensic evidence. Archive only when the artifact is stored and reachable elsewhere and the evidence provenance remains intact.

## Mandatory local cleanup handoff

After the remote shortlist is reviewed, inventory each local repo/worktree with read-only commands first: path, branch, HEAD, upstream, `git status --short --branch`, untracked files, active Python/MT5 runner process references, and evidence file sizes. Never run `git clean`, `reset --hard`, broad stash, or bulk delete. Propose local deletions separately for joint approval.

## Safe next step

Review candidates in small batches, run `compare_commits` for the specific target branch, check open/closed PR dependencies, record recovery SHA, then ask for explicit approval before each remote deletion batch.
