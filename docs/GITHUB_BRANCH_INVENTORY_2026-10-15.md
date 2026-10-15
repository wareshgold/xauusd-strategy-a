# GitHub Branch Inventory — 2026-10-15

Generated from GitHub REST branch refs and open PR metadata. Read-only inventory; no branch was changed by this report.

- Remote branches enumerated: **329**
- Open PRs returned by API: **54**
- Classification is heuristic based on branch name only. It is not a decision that the branch is safe to archive.
- All branches remain **REVIEW_REQUIRED** until ancestry, unique commits/files/evidence, PR dependencies, and local worktrees are checked.
- SHA is the exact remote branch HEAD observed during this inventory; it may advance later.

## Work-area counts (heuristic)

- Source Research: 200
- Forward Test: 47
- Backtest/Validation: 33
- Factory/Candidate Lab: 26
- Unclassified: 18
- Shared/Engineering (review): 3
- Default branch: 1
- Test/Infrastructure: 1

## Full branch list

| Branch | HEAD SHA | Heuristic area | Open PR(s) | Proposed status |
|---|---|---|---|---|
| `checkpoint/f13-before-forward-lifecycle-fix-2026-09-24` | `a9bf42c230843dc00767fcaed58061dc148dad14` | Forward Test | — | REVIEW_REQUIRED |
| `checkpoint/sp2l-xauusd-forward-ready-2026-09-24` | `e971013429156b79104f3267a2270936e87dcc5c` | Forward Test | — | REVIEW_REQUIRED |
| `chore/branch-governance-inventory-20261015` | `2add432a5c732629cdecc8bcf2673884c19d5da6` | Unclassified | #327 docs: establish safe branch governance and archive plan (draft) → main | REVIEW_REQUIRED |
| `dev/deterministic-engine-foundation-clean-2026-09-14` | `2ba192865a29cc6722ccc28097ffc4ec2af5e715` | Shared/Engineering (review) | #126 feat: isolated deterministic engine foundation (open) → main | REVIEW_REQUIRED |
| `dev/sp2l-deterministic-engine-foundation-2026-09-14` | `4d353fc24f11c17bb7a349af1af4bbaa1145f833` | Shared/Engineering (review) | — | REVIEW_REQUIRED |
| `diagnostics/forward-runner-silent-poll-20261015` | `ad78769983b9a12f2d5d98018959572f115036b4` | Forward Test | — | REVIEW_REQUIRED |
| `feat/factory-raw-m1-audit-candidate-lab-20261015` | `247c0d7a727fdfcfe34368b12ae3b49bfbe1ed5a` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `feat/factory-raw-m1-integrity-audit-20261015` | `4f3191e4471b803fbcbe448de3add3b54d250df7` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `feature/factory-external-strategy-comparison-20261008` | `040583f61f3f0f261eb5edf31a78c014cb642ac2` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/dashboard-open-closed-trades-20261008` | `749e41ef1c3b483887d3a0309bcbe6d7e01e146a` | Forward Test | — | REVIEW_REQUIRED |
| `fix/factory-append-lifecycle-guard-20261011` | `eb2feed895c73a5fb71b27ff11d2962a51cd16c6` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-empty-availability-windows-20261015` | `9ec2310276c014db2fce9decd07aa252aa1f2bae` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-lifecycle-conflict-audit-20261011` | `44620b8c4fe7986fe2ae25c870d8b7e17d728ea5` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-preserve-mt5-acquisition-bytes-20261011` | `67bdd65f77e25c45c49c02ee459002d03d8ed9b2` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-raw-m1-audit-local-regressions-20261015` | `7b8b02c64eacb54ae7fa53d4e29bd232a9741d51` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-raw-m1-line-ending-hash-20261015` | `a186cf7c888095ae1b4c54bb582c0d7088c1a089` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-raw-m1-normalization-escape-20261015` | `ff1c106d03ae94092f79788038f7c2a0364dc645` | Factory/Candidate Lab | #323 Fix CRLF normalization byte escapes in raw M1 audit (open) → research/factory-candidate-lab-20261010 | REVIEW_REQUIRED |
| `fix/factory-tick-acquisition-no-overwrite-20261014` | `44acabeba7a0cf5465046924e5b716553cd5ede5` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/factory-timestamp-audit-empty-csv-20261015` | `54fa07fe43033f8756987c5e6021c0d3b09faf09` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `fix/forward-pending-lifecycle-20261008` | `76dc9ffec8ddfd1ac642dd49b8fe60bb9d8aa0d8` | Forward Test | #285 fix(forward): normalize MT5 pending lifecycle collections (open) → research/sp2l-starnet-engine-integration-20261007 | REVIEW_REQUIRED |
| `fix/full-suite-baseline-regressions-20261014` | `7e79cae35e2c59b719df0ba765a00af14ae78b0d` | Shared/Engineering (review) | — | REVIEW_REQUIRED |
| `fix/phase38-register-script` | `53e06f73948b60735ab10efd3c58016c22728351` | Backtest/Validation | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-all-blocked-notifications-20261013` | `ab5a7400967d7206305e06d7da711b9b3910f23c` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-close-result-after-restart-20261013` | `9289497b2d4ae5860584620091c1b15b35b674ec` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-deal-history-position-query-20261014` | `41aa1f459aeb3a5b823349894583864fc1a16ac6` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-deal-lifecycle-clean` | `75956510f88e1be2dad9453719eb9dbf0ef5daec` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-deal-lifecycle-server-time` | `6311c949b561105e278a18209da47e15f4cab468` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-history-guards-preserve-pip-display-20261014` | `6b23005ef5dbfe05af257ae24ad53ea495c4190a` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-history-query-log-dedup-20261015` | `e4f3c3e476a4ed83c5bc6748441ced4e765e8274` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-history-query-position-only-20261015` | `31ef5590c2d4e4d25642bd93a00714d1f1bafd97` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-lifecycle-query-fail-guard-20261014` | `3957176d795115949d63617e39bff9c4fbc78893` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-lifecycle-reconciliation-guards-20261013` | `fb4f479f9d158f8e0baeee126f51be9e74efda34` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-market-data-diagnostics-20261013` | `f30b7cbcfa66dad88bc9e6b3ed205a1677191eaa` | Forward Test | #293 Add RR2/TRAIL4 market-data availability diagnostics (open) → fix/rr2-trail4-pending-lifecycle-safe-20261011 | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-clock-offset-20261015` | `26785b94943753be98acc9ded76238b7cd1806e8` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-lifecycle-exact-20261008` | `d037df165a99a4576ae915cffcf51fe1432fb938` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-lifecycle-list-20261008` | `9ed008d01f14c6cde70cc7a569ecf8037360670d` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-lifecycle-safe-20261011` | `c54fce17c5b6014031775812a517fa0c84eae626` | Forward Test | #288 fix(forward): make RR2 TRAIL4 pending expiry restart-safe (draft) → fix/rr2-trail4-pending-lifecycle-list-20261008 | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-lifecycle-tuple-20261008` | `ef39c3aa5792f26081504504a1066898edfe0bbf` | Forward Test | #284 fix(forward): normalize MT5 pending lifecycle collections (open) → research/sp2l-starnet-engine-integration-20261007 | REVIEW_REQUIRED |
| `fix/rr2-trail4-pending-safe-newlines-20261013` | `9fe921101f13ce77e22f370c0a6149b822f61b10` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-position-reconciliation-gap-20261013` | `8100e2444f9b33f61b39edf73b82b4340fa73f14` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-stale-telegram-deals-20261014` | `d2344e571bbb7d87fe11774268477b018a007244` | Forward Test | #302 fix(telegram): suppress stale MT5 lifecycle deal notifications (open) → fix/rr2-trail4-pending-lifecycle-safe-20261011 | REVIEW_REQUIRED |
| `fix/rr2-trail4-telegram-deal-time-20261013` | `d4e02164256872fe4bd240d66bdc3197e17f0fe3` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-telegram-newlines-20261013` | `8a3ad94ab61c974b3fd783d83f0f2ece0fefc565` | Forward Test | — | REVIEW_REQUIRED |
| `fix/rr2-trail4-v3-dashboard-data-20261015` | `210016d1ebc8f74b7e99f7544ca5c3f481838366` | Forward Test | — | REVIEW_REQUIRED |
| `fix/typescript-build-compatibility-phase12` | `306737513f3a3f44bc41664a5773092225c2fb00` | Backtest/Validation | — | REVIEW_REQUIRED |
| `hardening/forward-reconciliation-provenance-20261008` | `8a2f49fc100f6f0fa5df841bf9ae7a833c627018` | Forward Test | — | REVIEW_REQUIRED |
| `hardening/forward-session-lifecycle-identity-20261008` | `02a76a2fae97b524a2a88a3ce9a59c1f02df5166` | Forward Test | — | REVIEW_REQUIRED |
| `hardening/holdout-forward-provenance-20261008` | `b4be909fa2091c4093b8ad1bddbb94fab0059e1e` | Forward Test | — | REVIEW_REQUIRED |
| `main` | `6ac7db6ffa5101b42adfb96ece16674c4e9130bf` | Default branch | — | REVIEW_REQUIRED |
| `research/baseline-integrity-audit` | `bc29449168b479c55e694590a2a6e409e39c0246` | Unclassified | — | REVIEW_REQUIRED |
| `research/candidate-selection-competition` | `c097bfe4e20c8df83ff5733cc984b5a4145c766e` | Unclassified | — | REVIEW_REQUIRED |
| `research/checkpoint-2026-09-03-outcome-path` | `775fa61f2c8203409c33c33764be1e1c599416ec` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/dataset-split-v1-2026-09-09` | `0d99d6aa1c9d0666677b4698694ea75b09631bbd` | Unclassified | — | REVIEW_REQUIRED |
| `research/entry-edge-post-entry-path` | `a77f119ec55b465a5650f50b8a231a3c9cbdcc2f` | Unclassified | — | REVIEW_REQUIRED |
| `research/entry-edge-t1-exit-validation` | `0670abd602be040b835155dd21a68c3af339d6a8` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/entry-geometry-diagnostic-20261013` | `0cefdeeaf79bbcc426c456e2f3e2609da0434e1a` | Source Research | #297 [Research] Audit SP2L entry geometry against previous candle levels (draft) → research/trailing-matrix-audit-20261013 | REVIEW_REQUIRED |
| `research/entry-trigger-mechanics-dev-val` | `f0f6f1168d59e022601b396a4c3bd75f0bf7a837` | Unclassified | — | REVIEW_REQUIRED |
| `research/entry-trigger-root-cause` | `0a71e5fc126ec257eca5d7b48ad887cf4203de9f` | Unclassified | — | REVIEW_REQUIRED |
| `research/excursion-topology` | `c8d4a6ae89a2a0f282c31df4d82f9f5050c1c25d` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/factory-candidate-lab-20261010` | `cb741ff3768f27ac69923fca7ca3320cea89782c` | Factory/Candidate Lab | #287 feat(factory): add deterministic candidate lab for research optimization (draft) → research/sp2l-starnet-engine-integration-20261007 | REVIEW_REQUIRED |
| `research/factory-journal-audit-snapshot-20261014` | `a9c5a567399b39225f6b6e2aad1147b4c75a2295` | Factory/Candidate Lab | #306 Record Factory worker journal audit findings (2026-10-14) (draft) → research/xauusd-availability-integrity-gate-20261013 | REVIEW_REQUIRED |
| `research/factory-timestamp-sequence-audit-20261014` | `b8c6644be6ff45deaf84fb9a3fe4714cdbc2d157` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `research/infrastructure-audit-checkpoint-2026-09-14` | `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | Unclassified | — | REVIEW_REQUIRED |
| `research/ny-sell-preentry-discriminative-anatomy` | `8efaab929b96a753bfb2847b6a80a374fcf5ec36` | Unclassified | — | REVIEW_REQUIRED |
| `research/ny-sell-preentry-temporal-replication` | `f35f58ca246cb9b494e54ece2cd20a35899d305f` | Unclassified | — | REVIEW_REQUIRED |
| `research/outcome-path-stop-stress` | `c097bfe4e20c8df83ff5733cc984b5a4145c766e` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/outcome-stop-stress-excursion-v5` | `77618d93bbffc27f3bdaa03fc9d126bf78dc0079` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/pgap-source-resolution-v1` | `5ccd9c02459f71cee9eddb77bfcf8ff3c7cd6b71` | Source Research | — | REVIEW_REQUIRED |
| `research/phase12-preentry-geometry-robustness` | `ac06d232c95080afab8f6058e72278ac06b54c55` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase26-d-archetype-feature-decomposition` | `96951ddb9e9259fdd2952fd5acdae72a0d9a9b06` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase27-d-archetype-conditional-residual-decomposition` | `d8955cfec50662739d9a03984ded7f14b48b847a` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase28-d-archetype-conditional-validation` | `b21b2eabfc7fbb386f88a7fb41fd03056459fa41` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase29-d-archetype-residual-after-geometry` | `35426751c6ba64466ce114cf8c42d335430addd6` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase31-counterfactual-direction-flip-snapshot` | `550b3929a9824469ec174ad84fe0bfdcbbe8e0b6` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase32-directional-counterfactual-decomposition` | `c1c30e80eb80143683209c2a1b760763574ceee9` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase33-counterfactual-phase27-archetype-decomposition` | `a36ba7da9270196558c2885532c91fde2f116382` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase38-a-ny-temporal-stability` | `49952d907ec149c596c423c3d4bd0d27acd1bf00` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase42-expanded-data-validation` | `4a293ad645df4057ac5eed50569def7820036aae` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/phase42-full-history-expansion` | `b2c9b2f520a39d307a4e0c3de52550a9b9317c64` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/pr-branch-governance-audit-2026-09-14` | `e0941815943f4648bf8dc5ee00ecbd3838deaa2e` | Unclassified | — | REVIEW_REQUIRED |
| `research/raw-m1-synthetic-fixtures-20261015` | `b344534a7e6de63bfd3b32a564e89beab19ec218` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `research/rr2-trail4-session-vs-no-trailing-20261015` | `c14d96b3d2c65dc04e7e2741aba9dfbad6f8c9c6` | Forward Test | #315 Research: compare current RR2/TRAIL4, London-to-NY, and no trailing (draft) → fix/rr2-trail4-telegram-deal-time-20261013 | REVIEW_REQUIRED |
| `research/rr2-trail4-telegram-checkpoint-20261013` | `c3fe369c613fcaf43dd3a3e1b21e3e3b06fb989c` | Forward Test | — | REVIEW_REQUIRED |
| `research/rr2-trail4-trailing-matrix-20261013` | `a58c67614b341ab68aa2eb64d02a25d66750aa46` | Forward Test | — | REVIEW_REQUIRED |
| `research/source-aligned-sp2l-semantics-v1` | `9fad09a5b4e0ba1a829d156ce9af93b7eb50ab80` | Source Research | — | REVIEW_REQUIRED |
| `research/source-resolution-entry-level-v2` | `065893b5ece2dc2ecaf2d9755049a03b47a5cc3b` | Source Research | — | REVIEW_REQUIRED |
| `research/source-video-visual-evidence-2026-09-08` | `a12ffe3a6f4f8dcff9ac281891d3da1f881dad77` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-adjudication-execution-review-2026-09-15` | `0f90c166976153fc371d2b5e0f8efcb4be8ae404` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-adjudication-runbook-2026-09-15` | `fa8e823ce1993c923df6c50db198eaa660aa44af` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-adjudication-worksheet-2026-09-15` | `277037134d87053d2357e0ecdb37d7b108e57d83` | Source Research | #177 research: add executable human adjudication worksheet (open) → research/sp2l-manual-adjudication-gate-2026-09-15 | REVIEW_REQUIRED |
| `research/sp2l-api-export-equivalence-2026-09-21` | `75710abb104c18ab9a7f95097c3cc77362900121` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-author-implementation-crosswalk-batch38-2026-09-17` | `e8e867be6aec56b3390c4566c2bdd36f8980cf2f` | Source Research | #231 research: Batch38 author implementation crosswalk (draft) → research/sp2l-pgap-forensic-batch37-2026-09-17 | REVIEW_REQUIRED |
| `research/sp2l-author-replica-backtest-batch40-2026-09-17` | `b2249e0e1af03646411d728cf8298552960db5cf` | Backtest/Validation | #233 research: author replica candidate backtest harness (draft) → research/sp2l-f14-abcd-primary-video-batch39-2026-09-17 | REVIEW_REQUIRED |
| `research/sp2l-author-site-f13-source-update-2026-09-21` | `c66fcb36dafa3d7f4ea6d97cc6d2a01f465b2c37` | Source Research | #255 research: record author-site F13/F12 source evidence (open) → research/sp2l-complete-unresolved-synthetic-fixtures-2026-09-21 | REVIEW_REQUIRED |
| `research/sp2l-batch46-source-blocker-closure-2026-09-21` | `c19a0eb2418a1189caf553a9a7d80a4980960744` | Source Research | #251 Research: Batch46 remaining source blocker closure pass (draft) → main | REVIEW_REQUIRED |
| `research/sp2l-candidate-events-2026-09-15` | `7137aa19c77421d41dc0f6d91b8138ec0dc8da68` | Source Research | #194 research: candidate event fixture contract without geometry inference (draft) → main | REVIEW_REQUIRED |
| `research/sp2l-candidate-sandbox-g55-2026-09-09` | `e1267d22556ee255dc99e0cd181ae9a7b4fdecdd` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-canonical-gate-enforcement-2026-09-16` | `344db899a8d4d41a41f29d85e2ca0aa677cd4f1e` | Source Research | #213 test: enforce frozen-geometry boundary before canonical backtest (draft) → research/sp2l-f8-f12-f16-chain-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-ci-integrity-g47-2026-09-09` | `f4490c0a5debbb01cf954f70745a238c62086275` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-clean-forward-xau-eurusd-usdjpy-20260928` | `aa86bdd2ad2d342d83576acb2875767271d51dd4` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-complete-unresolved-synthetic-fixtures-2026-09-21` | `690eaf0fa889d8a440b2e4ec8e03dd7de8a8036b` | Source Research | #254 research: complete unresolved synthetic fixture gate (open) → research/sp2l-remaining-source-blockers-f08-f13-2026-09-21 | REVIEW_REQUIRED |
| `research/sp2l-current-state-snapshot-2026-09-15` | `50b05111ff12c23756306365bd1a423630454a3f` | Source Research | #173 research: record current SP2L project state snapshot (open) → main | REVIEW_REQUIRED |
| `research/sp2l-data-acquisition-g42-2026-09-09` | `09acac56ab5f59b710640b72a3f38d8087fa0f7b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-data-adapter-g41-2026-09-09` | `0b1c2ea89d5a3c810146d12fd06c9ef7d84249b9` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-data-architecture-contract-2026-09-15` | `bf721f95459b25221a5c3fa2524d07221f11d3cc` | Source Research | #184 engineering: define SP2L research versus MT5 data architecture (open) → main | REVIEW_REQUIRED |
| `research/sp2l-data-plane-gate-2026-09-15` | `886e462ec7a6163b39ef089da459cb4bdb15bd17` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-data-splits-clustering-g34-2026-09-09` | `b1ee08db3be7ff6c5d5cff90a6c40b4613d59377` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-discriminator-hunt-ledger-2026-09-15` | `01f8b5295625ce167022c0aa8518045bd910c713` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-entry-geometry-forensic-2026-09-16` | `e9560bc51e659316996b032dfe5570b1de898f5f` | Source Research | #226 research: worked-trade entry geometry forensic (draft) → research/sp2l-worked-trade-timeline-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-entry-resolution-pass-2026-09-14` | `192f800173f3833207ae53876813c245632af2d2` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-event-layer-2026-09-15` | `19a0db82519158f685d65b2e7f0234099f03c55a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-evidence-boundary-audit-2026-09-14` | `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f10-stop-boundary-fixture-2026-09-14` | `aa84f2881051e751e904d13db71b6ea8edb2a282` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f12-f15-adjudication-2026-09-14` | `81239dd84613105dd92431418b7c94fd348d023a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f12-trigger-family-fixture-2026-09-14` | `ca63ddafc11f66681c2c7000054303583576ef2f` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f13-2x-synthetic-fixtures-2026-09-21` | `d5f308cbf04b6dad3909dc1734bed0377ec65be8` | Source Research | #256 research: add F13 2X synthetic fixture gate (open) → research/sp2l-author-site-f13-source-update-2026-09-21 | REVIEW_REQUIRED |
| `research/sp2l-f13-2x-tp1-fixture-2026-09-14` | `025261ac47e1eb9091695a559835cc9f1eac0d32` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f13-demo-forward-slfixed-2026-09-21` | `66d70b8ccebbba2bc34b5cc8e648fde98af60e96` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-f13-forensic-repro-2026-09-26` | `5d776b41caf84382980a02a5553e58c64448db81` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f13-source-reconciliation-2026-09-21` | `366ad624fff122f6fb197f69ca634154bcf7ea09` | Source Research | #257 research: reconcile F13 2X source anchors (open) → research/sp2l-f13-2x-synthetic-fixtures-2026-09-21 | REVIEW_REQUIRED |
| `research/sp2l-f14-abcd-anchor-fixture-2026-09-14` | `4040c0aac64b03efa4e89220a9f592510a722792` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f14-abcd-primary-video-batch39-2026-09-17` | `7067fe6b99c43fe2737f7a16d07eef54eef162bf` | Source Research | #232 research: Batch39 F14 AB=CD primary-video forensic (draft) → research/sp2l-author-implementation-crosswalk-batch38-2026-09-17 | REVIEW_REQUIRED |
| `research/sp2l-f15-bearish-mirror-2026-09-16` | `31731968be5e7c901032ff74670be1ced92a93b6` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f15-bearish-mirror-fixture-2026-09-14` | `0839bb7db1040d91e1ccb2f250fae095db2a0576` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f8-f11-source-resolution-2026-09-16` | `d2113fc178eb9f0b77a69a1ac4ac1bd303578740` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-f8-f12-f16-chain-forensic-2026-09-16` | `7c8e53a13cb3788a7402a3c5f28543f387a36de9` | Source Research | #211 research: F8 F12 F16 chain forensic evidence (draft) → research/sp2l-primary-artifact-f14-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-final-source-boundary-unresolved-fixtures-2026-09-21` | `b39fab5438104a55ab3866c95ea4ae7580b9a263` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-fixed-snapshot-stability-2026-09-17` | `2ffb544c8db4edf56de3e9e31f1d098c67ea9d9c` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-fixture-contracts-v1` | `ba748f57e7750ee126d6d512908706e77879cc1a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-forward-missed-signal-audit-2026-09-21` | `3611aacdf74eab258ddbd940857db0412963374e` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-forward-observed-evidence-20261008` | `f9a055496c46842fc6ded0893d6db78ffa86e1e4` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-forward-observed-report-20261008` | `1fc44fd2152ce414a705324372cf75058ad997e2` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-forward-reconciliation-fix-2026-09-21` | `0a500203fedf60193b31ca00037c37122c6be407` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-freeze-decision-gate-2026-09-15` | `dc6f5a0790d524a62e465d78b3863cd6fc424420` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-frozen-geometry-contract-2026-09-14` | `8bf4c45b26ac03063c913fba2d33cf4ab9b10d58` | Source Research | #156 research: establish SP2L frozen-geometry contract (open) → main | REVIEW_REQUIRED |
| `research/sp2l-frozen-geometry-gate-pr-2026-09-16` | `76430ca06579087ab97eba07ed4bd462f127f0be` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-frozen-geometry-readiness-2026-09-14` | `33bc97e5788f6dfb38c5ecf01df632b423337d15` | Source Research | #157 research: establish SP2L frozen-geometry readiness gate (open) → main | REVIEW_REQUIRED |
| `research/sp2l-g101-g103-recovery-guard-2026-09-10` | `328cacde075bbf36c8f292b644db3c10522ac880` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g104-g106-recovery-idempotency-2026-09-10` | `8631fc29eadb81c93deb4e79be060b23cac31dd7` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g107-g109-recovery-replay-2026-09-10` | `30d0d9b5ead842c62f94c74326b571817856b6b6` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g110-g118-batched-recovery-safety-2026-09-10` | `17b679c15edbc837f284051eefef7f86671543a9` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g119-g127-batched-integrity-safety-2026-09-10` | `f93bed7846a50000c4e69df6bdc1690b79d6fce8` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g128-g136-batched-research-hygiene-2026-09-10` | `6ad54b1f468fd1f81db5359b3fb1d07b9dafafb2` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g137-g145-batched-validation-boundary-2026-09-10` | `9fc1bcf55b1435ca4cd157c7e13cebfc9459f9d3` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g146-g154-batched-validation-evidence-2026-09-10` | `2c7a6a00adb85ec9b9ee39f27454f700a2dbc5f4` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g155-g163-batched-research-audit-2026-09-10` | `aaf0cff8247ea7638e19eb8f9d4ba2bb1a0f42a4` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g164-g172-batched-reproducibility-2026-09-10` | `1bee5b80cb243aefbeaf70564a52d49a1be62ad4` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g173-g181-batched-validation-ledger-2026-09-10` | `4040e9eeb7299f4198217b80d978ad8031771901` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g182-g190-batched-holdout-boundary-2026-09-10` | `5ab99d5b04247b65b1457b98455e77def4ba4b6e` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g191-g199-fresh-holdout-integrity-2026-09-10` | `af40404e73d744fd9474ef9c3de481ec967f917e` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g299-geometry-reconciliation` | `49952d907ec149c596c423c3d4bd0d27acd1bf00` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g305-source-acquisition` | `2cb91350f0a85910d96ad47b56090153c78efad3` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g305-source-acquisition-final` | `f6b6fb5051a953e737985879bfec4281c52d850e` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g327-source-derived-target-fixtures-2026-09-12` | `5d00f101167df8b44d69b4353a43439f9628cf4e` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g329-source-visual-coordinate-audit-2026-09-12` | `cf321554dced15c63bf3b00cd89854393ad7a2f1` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g332-numeric-annotation-source-bridge-2026-09-12` | `1fa5b4191fd79614b620f5e41cd6a37a4edb3be2` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g333-entry-leg-visual-audit-2026-09-12` | `5074e09f9fa1bfe6b111c3b1b2b5b0e64cea4c40` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g334-abcd-anchor-audit-2026-09-12` | `8904d5fcdbc21a0e79d145094ee7d5f3d554820f` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g335-risk-reward-source-audit-2026-09-12` | `b8b8898f2629c3abcf05daf11d76a2c0eb7185b5` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g336-abcd-anchor-semantics-audit-2026-09-12` | `1d439391616e95c2a037310469b9c40559c0b657` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g337-wick-body-anchor-source-audit-2026-09-12` | `d617b812822cec190f4b1ff754a556bfc661a192` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g338-structural-anchor-event-source-audit-2026-09-12` | `ecdead209e0423de4abd3567f7d4af3679c990fd` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g339-synthetic-structural-model-discrimination-2026-09-12` | `e533b95a31718f5129698c3fd7fe43d4daa96d4b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g341-abcd-competing-model-synthetic-2026-09-12` | `dc7f6c186a9d8f4ab1a42f8a5d5d159d8f1214ae` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g342-abcd-adversarial-discrimination-2026-09-12` | `5ef3b1a36e8494373e5df2e5ccfb995d7fae2969` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g343-abcd-model-completeness-matrix-2026-09-12` | `cdb5b61e73282105a637bb5c248cb46589d39125` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g344-minimal-pair-discrimination-2026-09-12` | `00ebb2434626424bfee55432246c6bc66d163ace` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g346-source-evidence-gap-hunt-2026-09-12` | `6178c94a1822469adb68808a9ade162b3f0625ed` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g346-source-evidence-gap-hunt-v17` | `325431f70df928206d64dfc98a818ad11c48a5da` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g347-parameterized-synthetic-geometry-research-2026-09-12` | `c7396d5aac229b5521dcb1d256acc502604ea3d0` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g348-source-resolution-closure-2026-09-12` | `b3469241a200434911020626497376a54274f2c7` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g349-official-web-source-bridge-2026-09-12` | `4ff65ab126bc382ff2ec539e88a0ff9432975e25` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g352-transcript-deep-source-audit-2026-09-12` | `055399df7df957ab319218a90cbd7fd13b37f78d` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g353-pgap-pressure-gap-video-bridge-2026-09-12` | `48e75d4b1b4da672c87ea93ef8abec06774b02a8` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g354-pgap-geometry-cross-reference-2026-09-12` | `8dfee272deca689e164ca574e78c1ff5ca8197fa` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g355-pgap-synthetic-discrimination-2026-09-12` | `252c7b7a8e5ea92f70059889712d9cf5e4477192` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g356-pressure-gap-geometry-audit-2026-09-12` | `72133ee57584135d99a4e5c9c7871e73b5ad4a45` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g357-official-page-reconciliation-2026-09-12` | `e54ab15dc766cfefa7c8953c09aff78844dc3759` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g360-results-2026-09-12` | `67397a8a2b4e59f05301bd97c1872df490ec9ea2` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g361-geometry-freeze-decision-2026-09-12` | `33c55604c5954061e2dd47301405b7ca9dab6288` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g364-source-artifact-acquisition-2026-09-12` | `a3731aeee903fe5cb8f5a2c3b0403259b28117bc` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g369-adversarial-fixtures-2026-09-12` | `4ffdfd2e9100eb5adf3dce1f3b305c75993339ee` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g371-targeted-source-resolution-2026-09-12` | `104546041f13021a9ad0dd5252edaf8854433157` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g375-hypothesis-execution-2026-09-13` | `beb7397f65f314c8028c703a1006e2021a0310fc` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g376-machine-fixture-runner-2026-09-13` | `e58dbd8ffc87897c99ba65e1d826ed41c1afaa47` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g377-official-geometry-reconciliation-2026-09-13` | `e82bb4ba4e5993ac3eb6c99e944e0596f2028a9e` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g378-source-closure-2026-09-13` | `cf986ecf4bc913b8f30865ef770ad47332676234` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g379-hypothesis-execution-2026-09-13` | `2857ad4ca00126b4ce480147ef0e99e20892dfde` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g380-synthetic-counterfactuals-2026-09-13` | `5c17065d7b8dc72f1ffe8ae34397cfd27f2ab5f9` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g381-discrimination-consolidation-2026-09-13` | `3fcb84ac6e3126f28fd2f1e6977f978a67231cb2` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g382-state-matrix-2026-09-13` | `d830d9dc9971ead7fdf758553c9f0db89ce50a14` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g383-minimal-pair-coverage-2026-09-13` | `0600a39542be13f4cba0ea6c404d0afaeb774e9d` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g384-source-closure-matrix-2026-09-13` | `61052a8199a3fe88470b17776366cf8a3b87c458` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g385-semantic-core-dev-harness-2026-09-13` | `1deeaaf72ebfa54aabd3778e95837ca733c9086a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g386-dev-harness-2026-09-13` | `523bed70d0c935664a8d80e59c3f8c10c516bf12` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g388-dataset-runner-2026-09-13` | `c50f3d442fdc720534c354552bf26f3f4cbaa2bf` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g413-source-geometry-reconciliation-2026-09-14` | `67fb8a2847daf973e8df83224a9074fce9ab0df3` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g45-reproducible-dataset-2026-09-09` | `19f7aa22a62e8a2ae4623c0927f74d0475e4696b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g48-live-acquisition-2026-09-09` | `a6b6b98ee06c32021090424b9c8bcf9db2e27758` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g49-historical-coverage-2026-09-09` | `eae644e0782c724414121745eec4f77435939a92` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g56-cleanup-2026-09-09` | `0b2038e6ca9339b6505ab2c855cea7580eafd884` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g56-source-discrimination-review-2026-09-09` | `af2388104de69bd8d8056c5ed3fa26420978c15b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g57-evidence-fixture-map-2026-09-09` | `f368608b4201ff08205a8fde4fffdf12b76b5340` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g58-frame-level-audit-2026-09-09` | `fb72e915b8e62782e3c3e90c72c97b5c3fc1f03f` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g59-g60-discrimination-gate-2026-09-09` | `4d8c4c11b20c644a0854e908382a8e5cd5e3c9cf` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g61-g62-targeted-resolution-2026-09-09` | `a43b075304e3f5025f794984b8043af269d577ef` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g63-g64-source-closure-2026-09-09` | `44a5bc3d5ac7dd32c752062f889166105cf0de7c` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g65-g67-parallel-readiness-2026-09-09` | `498548a045e6073be0d17ed9abc6d9a8c10a22a3` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g68-neutral-research-tracks-2026-09-09` | `d3fb786520d16a80bc9ebfee95f5eae315066616` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g69-neutral-baseline-stability-2026-09-09` | `c3272b23b8278b83c89a46a21b052bfa8d366177` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g71-g73-demo-execution-safety-2026-09-09` | `957fb3b591a400eaf53934273e941f8de5a6a07c` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g74-g76-demo-reconciliation-safety-2026-09-09` | `fe53b1de99eba3d7f65743c3355ab6a84625beca` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g80-g82-demo-state-idempotency-recovery-2026-09-09` | `f2ccaa7bee50a45fbc677252c45a6889b9cae4e8` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g83-g85-demo-recovery-journal-2026-09-09` | `7f527875477c46f3266896ca389b9718ada7e914` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g86-g88-demo-journal-integrity-2026-09-10` | `1e440aa00b644c6cdea9a575af1b5b22f9d804c3` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g89-g91-replay-recovery-audit-2026-09-10` | `cf03167dcdec0e9aa3bf5e62c569ae48002e5e8e` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-g92-g94-demo-observability-2026-09-10` | `e403d3db245996c878187dccb6869b63cd64ba8d` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g95-g97-demo-safety-rehearsal-2026-09-10` | `bed6696541cd0793b00311e5bae34138571def8b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-g98-g100-integrity-boundary-2026-09-10` | `9b4103735c77e1f410da89c49d2d236ad8882707` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-gate-coverage-hardening-2026-09-16` | `bbacbec17742b37fc6d1f927a23f6404eda031f4` | Source Research | #212 test: harden SP2L frozen-gate blocker coverage (draft) → research/sp2l-f8-f12-f16-chain-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-gate-preparation-final` | `851ae2eef29c1e909a364f1f4790d32d90b27f43` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-geometry-atlas-g29-2026-09-09` | `a0458c79e5a10e3637d5cbdcb3d77b6147107319` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-infra-regime-g33-2026-09-09` | `cd16489450e7c252a4b6626bdeb17b7459f9a161` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-leg1-synthetic-discrimination-2026-09-17` | `dc868c88395c938fad024fddd208c875e4ba764b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-legacy-mirror-backtest-20260929` | `0767bfa67ac86ab15f4ccca35b7a08ac128219be` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-live-mt5-telegram-2026-09-19` | `22b437fb86600356aa4e315da3a95da200e8500c` | Forward Test | #235 research: prepare guarded live MT5 + Telegram gateway (draft) → research/sp2l-mt5-session-matrix-2026-09-17-x | REVIEW_REQUIRED |
| `research/sp2l-manual-adjudication-gate-2026-09-15` | `8d14e66e25049be592ca512313e430b282e4268e` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-acquisition-audit-2026-09-17` | `ec3b407aa41464a4ae80afc269ca4b83d689855c` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-acquisition-audit-2026-09-17-b` | `d9d76795fe0006189e48cf2819290ce2b9ff7268` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-acquisition-audit-2026-09-17-c` | `aca366ebe81fd98387f9c0fa2e94014197b59330` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-copy-rates-boundary-validation-2026-09-21` | `0a4f0585ef59946db398cd44dc0c626c4865b6fc` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-fixed-snapshot-2026-09-17` | `254478a6e0ce21a08215508b991ae19b234aab6c` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-independent-export-equivalence-2026-09-21` | `ad1ef4ce7aa2d787e0701587806ccb88a643453b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-mt5-session-matrix-2026-09-17-x` | `7fd80a93cdad3f25a7b8a02d02603d5208ef5de6` | Source Research | #236 research: MT5 session matrix, acquisition pipeline, and provenance research (open) → main | REVIEW_REQUIRED |
| `research/sp2l-mt5-symbol-discovery-2026-09-17` | `100abc6aff0b3f5cef016cbe0a257d1a09ffed57` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-multi-symbol-condition-diagnostics-2026-09-22` | `e67b69d375c1c40629ea08b69c2a7715c4d7931f` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-p1-f11-f12-source-resolution-2026-09-16` | `435a59567d858890d884adf6942d761ed9c66a3e` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-pgap-candidate-sl-shadow-spread-2026-09-21` | `8e3e5f79356940028b1a314d47f9929b37d65775` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-pgap-forensic-batch36-2026-09-17` | `539be81dc2a2a5a8eca44a403431738699280bdd` | Source Research | #229 research: Batch36 P-Gap forensic source resolution (draft) → research/sp2l-source-resolution-pgap-2x-2026-09-17 | REVIEW_REQUIRED |
| `research/sp2l-pgap-forensic-batch37-2026-09-17` | `6b4bb4d18cbee5b50cf4c1885c231bd529bdf421` | Source Research | #230 research: Batch37 P-Gap mirror/indexing negative-resolution (draft) → research/sp2l-pgap-forensic-batch36-2026-09-17 | REVIEW_REQUIRED |
| `research/sp2l-pgap-source-aligned-2026-09-26` | `8a244894ed16a3ff26c0e776e5434c6b537dc82a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-pgap-source-reconstruction-2026-09-21` | `051ac79517501b821daf49d67ef08b9f36f8a7c8` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-pgap-source-resolution-2026-09-14` | `25a9e249d56ef06937545c73f4c18d57657c468b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-pgap-source-resolution-2026-09-16` | `d331f1774b4a32b583757efe3fb163c7b9a4bb0b` | Source Research | #214 research: P-Gap source-resolution candidate ledger (draft) → research/sp2l-f8-f12-f16-chain-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-pgap-synthetic-fixtures-2026-09-21` | `2d8b527b3222e7ad0564b1fef2247d0bacd0309e` | Source Research | #261 research: extend SP2L source reconstruction with AB=CD discrimination (open) → main; #260 research: add P-Gap source reconstruction synthetic fixtures (open) → research/sp2l-pgap-source-reconstruction-2026-09-21 | REVIEW_REQUIRED |
| `research/sp2l-primary-artifact-extraction-2026-09-17` | `818e831597776061745d8660e3e6f965fecf61e0` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-primary-artifact-f14-forensic-2026-09-16` | `13487b4c2ddcce142a4c93918c99fc1f8a1e5cf0` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-primary-artifact-forensic-2026-09-16` | `d47f6b0d5ffe0043f6d6f4ab231f1a5c1f18a744` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-primary-sequence-geometry-forensic-2026-09-17` | `d7b5b465832de6beb4bc0609326f978d90ce4799` | Source Research | #227 research: Batch 34 primary SP2L sequence geometry forensic (draft) → research/sp2l-entry-geometry-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-r-mapping-source-gate-20261008` | `b61e11137aab9d82f89ed67f0d8392c4b86b8e0f` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-readiness-dashboard-2026-09-15` | `ac9f56b82607bebe886b5d5bc4228a933b46f1ec` | Forward Test | #176 research: add SP2L readiness dashboard (open) → research/sp2l-current-state-snapshot-2026-09-15 | REVIEW_REQUIRED |
| `research/sp2l-real-sample-g44-2026-09-09` | `cbd4b35910ea2c8a88a49e1bb323cdc07dbf3082` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-recent-4week-test-2026-09-17` | `1e6a183cefd01a14a48a076008ccf4bed0258a55` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-remaining-source-blockers-f08-f13-2026-09-21` | `8d0e9279f5701e069432f23a4ae0e8a32716dc8b` | Source Research | #252 research: consolidate remaining source blockers F08-F13 (draft) → main | REVIEW_REQUIRED |
| `research/sp2l-research-readiness-g51-54-2026-09-09` | `ad5ac7d640cbcbcf9bd34b125cf2f833636d3670` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-risk-boundary-f10-2026-09-09` | `2509cb05d62a85ca52d4e23c88de48ae35369d3b` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-rr2-trail4-daily-replay-20261008` | `e6cf48f3e67147a6933893465a5a00f7d4f34481` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-semantic-contract-freeze-2026-09-08` | `5ccd9c02459f71cee9eddb77bfcf8ff3c7cd6b71` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-semantic-contract-freeze-2026-09-08-v2` | `5337f1b0446d33502fa206fa60542fa477412aec` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-semantic-freeze-g27-2026-09-09` | `a44ede0a9955650d4140c103ac90fdeed6df5ea9` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-session-aware-acquisition-2026-09-17` | `cabf406c3235d505798bddb8d9e1301fddf4789d` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-session-calendar-contract-2026-09-17` | `83cbb72c799b4175a6a5569c5f2bd6b8193b8862` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-sl-invalidation-source-resolution-2026-09-14` | `eafb6acb80f2d2f714855e4c4f93d0eb57299257` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/sp2l-source-adjudication-f8-f11-2026-09-14` | `2ba192865a29cc6722ccc28097ffc4ec2af5e715` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-boundary-fixture-plan-2026-09-21` | `cf5fc14f6dc6db3d6f54d051b9a5e7305b0989d6` | Source Research | #263 research: freeze source boundary and unresolved fixture plan (draft) → main | REVIEW_REQUIRED |
| `research/sp2l-source-candidate-pgap-sl-2026-09-22` | `d62caa6f596a709e663850d1b6c709c38f5f1eae` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-closeout-2026-09-16` | `a1387a9ef48d0ba0a840b5fd3afc8c49fc416f88` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-closure-g39-2026-09-09` | `6cc4503dd72e4bc6e27be3e217aeee271eef6b3a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-closure-g40-2026-09-09` | `00aaa201a4d7331c2d21075cb65baa1497813660` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-discrimination-g37-2026-09-09` | `6247848ba807387ac058d9e715945dc7531c65db` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-discrimination-g37-run` | `c83d03fd35a4ba51903df8028a137635a5439243` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-batch-2026-09-14` | `f53306122cec592ec5dc9cc3ce469b47c3eed34f` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-checkpoint-clean-2026-09-14` | `12f68715aafcba43f8431b1f04053b7a272f1475` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-consolidation-2026-09-14` | `43934a0625b7cae0182e83451b836fe2e53c783a` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-f18-f20-2026-09-09` | `e7ab4d74a20da544c1cd0009aa02e678c8c21eac` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-pgap-2x-2026-09-17` | `e377695d77aa81141df189a96bc545fe828635c1` | Source Research | #228 research: Batch 35 official-source P-Gap and 2X resolution (draft) → research/sp2l-primary-sequence-geometry-forensic-2026-09-17 | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-priority-pass-2026-09-14` | `5de4213ba03b873b7cfad96f32ae0922587dfa44` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-stop-condition-2026-09-14` | `b52fc6bc98c349bdaf604fa9b1d1284f5decd9b2` | Source Research | #147 research: establish finite SP2L source-resolution stop condition (open) → main | REVIEW_REQUIRED |
| `research/sp2l-source-resolution-v2-2026-09-09` | `289e50f476dbd7d3052abe01018d2b3946949c02` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-source-safe-replay-2026-09-15` | `6f20c8aa1e12b1dca0af405a84732f769c5c7932` | Backtest/Validation | #158 research: add source-safe SP2L replay harness (open) → research/sp2l-synthetic-fixture-contract-2026-09-14 | REVIEW_REQUIRED |
| `research/sp2l-source-video-frame-audit-2026-09-15` | `be1afb9bf41f757463af5e91bfaef1351264567b` | Source Research | #185 research: persist source-video frame audit and SP2L continuity snapshot (open) → main | REVIEW_REQUIRED |
| `research/sp2l-source-visual-resolution-2026-09-17` | `87ec09db5d7dfb977c884303d92dd68f171d62d7` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-spec-kit-adoption-2026-09-15` | `96843f9050f4c9f7857dc006e7d94e440a5ee364` | Source Research | #164 research: assess GitHub Spec Kit adoption for SP2L (open) → main | REVIEW_REQUIRED |
| `research/sp2l-spec-kit-pilot-coverage-2026-09-15` | `49d87dc0f3885689b61d5f01f0b678e2e8280d21` | Source Research | #165 engineering: run non-canonical Spec Kit pilot for coverage infrastructure (open) → main | REVIEW_REQUIRED |
| `research/sp2l-starnet-engine-integration-20261007` | `befec09c752e8d7ba9d10ff75d4e39ad5351c853` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `research/sp2l-strategy-a-v2-2026-09-27` | `b75c59d5c752d87df290dd5d99f2d2d8e3d3d896` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-strategy-a-v3-1-monitoring-20261001` | `7a1916b6fa74c1902b849351827deb5c2948ad53` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-strategy-a-v3-trailing10-20261001` | `b048ed3f2c36eecc0a8abf6fa140ea947894ceca` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-strategy-research-factory-20261006` | `cb65e6c107f978c891f6d98c3f017a6ca4c51f31` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `research/sp2l-synthetic-fixture-contract-2026-09-14` | `24f3b6301284d34a5cb08786adfb8e66f30f01ce` | Source Research | #155 research: implement source-safe SP2L synthetic fixture contract (open) → main | REVIEW_REQUIRED |
| `research/sp2l-synthetic-runner-g35-2026-09-09` | `8a24bfcd13ab0be819e620e59931e26e050af824` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-telegram-format-checkpoint-2026-09-21` | `1c6717007bb21de0110873e2bb71d215d265d31d` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-telegram-format-implementation-2026-09-21` | `a01c974e38cb32dd31cc6b1649ab024c4953a767` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-telegram-result-reconciliation-2026-09-21` | `80d9e906ebad85f2c04da7d2540f9fb09895d27f` | Forward Test | #244 feat: notify Telegram from reconciled MT5 TP SL exits (draft) → research/sp2l-telegram-format-implementation-2026-09-21 | REVIEW_REQUIRED |
| `research/sp2l-temporal-stability-snapshots-2026-09-17` | `07615a2a0974fbb410ab5ac9859f748ddc9304d5` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-trading-window-config-2026-09-17` | `0829325c7680f9a28b3171a113f73b855f519300` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-transcript-cross-resolution-2026-09-14` | `18019ca7631fbe5726583ba334f0eecf8c3d00db` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-transcript-cross-resolution-clean-2026-09-14` | `825cb4b007ad4b4ad88d0519efaa8db918bd940a` | Source Research | #151 research: cross-resolve authoritative SP2L transcript (open) → main | REVIEW_REQUIRED |
| `research/sp2l-trigger-order-lifecycle-forensic-2026-09-16` | `efa701fac51205d60f2e7200eb98e46b4fe938e5` | Source Research | #222 research: primary trigger and order-lifecycle forensic pass (draft) → research/sp2l-pgap-source-resolution-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-v3-forward-reconciliation-20261003` | `23029a97f2551a45ddca6433718628394266f1cc` | Forward Test | — | REVIEW_REQUIRED |
| `research/sp2l-v3-profit-optimizer-20261006` | `58f182d08b6d32810f2a03a747001b4278d70bb5` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-video-source-extraction-2026-09-14` | `9c9669e87b9e8ab6531c73ec09af8741332c61d4` | Source Research | #149 research: record direct SP2L source-video frame extraction (open) → main | REVIEW_REQUIRED |
| `research/sp2l-visual-geometry-v3-2026-09-09` | `318d4f08422cb350f002277cb390b01ffcce5eda` | Source Research | — | REVIEW_REQUIRED |
| `research/sp2l-worked-trade-forensic-2026-09-16` | `c237b2e91378f8720549908c0286df3d4d9b47d9` | Source Research | #223 research: worked-trade execution semantics forensic pass (draft) → research/sp2l-trigger-order-lifecycle-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/sp2l-worked-trade-timeline-forensic-2026-09-16` | `ddf465603244c0c53cae207cf3e8462f2682874d` | Source Research | #225 research: worked-trade chart/history timeline reconstruction (draft) → research/sp2l-worked-trade-forensic-2026-09-16 | REVIEW_REQUIRED |
| `research/spike-opportunity-window` | `8228fa484da30b3210e125efb96b319976ab0567` | Unclassified | — | REVIEW_REQUIRED |
| `research/strategy-a-poorsamadi-alignment` | `9d66169534875fcdf20c6e3176cdc0ef5682c4e6` | Unclassified | — | REVIEW_REQUIRED |
| `research/strategy-a-poorsamadi-geometry` | `90319b27e0defaa33e31f354a9585e5c718b6f1d` | Source Research | — | REVIEW_REQUIRED |
| `research/strategy-a-poorsamadi-geometry-density-audit` | `472b5a5f5f40137c53946894239fd2b2780bf6ef` | Source Research | — | REVIEW_REQUIRED |
| `research/strategy-a-poorsamadi-geometry-next` | `432d45c6523e223cce17aace99cacb6842f287fb` | Source Research | — | REVIEW_REQUIRED |
| `research/test-temp-2026-09-16` | `dedbbf1b10ad9f5457318434efedae3a6569a0ce` | Unclassified | — | REVIEW_REQUIRED |
| `research/trailing-matrix-audit-20261013` | `095666a1d3dfa588b635e66e630189a81fc779e3` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/trigger-failure-ordering-v2` | `413310e17f9087b67ed2599db14681ca4eaefcfe` | Unclassified | — | REVIEW_REQUIRED |
| `research/trigger-reclaim-mechanics` | `0665116d5917885e2eca1fcbce92af2c1621df70` | Unclassified | — | REVIEW_REQUIRED |
| `research/twelvedata-discovery-v1` | `b2f39e18398d7a2ffd94da0860e4cb109c11acb6` | Unclassified | — | REVIEW_REQUIRED |
| `research/volatility-hypothesis-holdout` | `ff337b4c17605c78ed0314895db3c4917c6e56d8` | Backtest/Validation | — | REVIEW_REQUIRED |
| `research/xauusd-availability-integrity-gate-20261013` | `c7b9d6e49c66af567ae4fced952d8606fcad9830` | Unclassified | — | REVIEW_REQUIRED |
| `snapshot/2026-08-31-opportunity-forensics` | `d90350f08ce809ea596400ac46cf321ea4c17056` | Source Research | — | REVIEW_REQUIRED |
| `snapshot/replay-backtest-audit-2026-09-14` | `70682823bd6915a8302d31680a453611240d67be` | Backtest/Validation | — | REVIEW_REQUIRED |
| `snapshot/sp2l-rr2-trail4-dashboard-20261008` | `6ee250a4b192bcb4f16eb8dfe8ad1bb1d221e170` | Forward Test | — | REVIEW_REQUIRED |
| `test/factory-forward-runtime-fail-closed-20261008` | `84c4f6f4da922ca8ef891aca82712a308a9c513a` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-fresh-holdout-forward-boundary-20261008` | `b98945368b71c587bdf529dff54b7ac53b3e8800` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-full-provenance-e2e-20261008` | `3db15d000c9199794d7e9001ddd0882a4f0999dc` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-holdout-forward-e2e-20261008` | `1c7a85c9f3e86956cac4ce0048fdb8e8c48f0b28` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-provenance-negative-hardening-20261008` | `4d5756458a62f9bd274a7181def83cf54650b085` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-robustness-holdout-boundary-20261008` | `37df87d13a641832c089e942f2ee6f20775040b0` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-untouched-validation-boundary-20261008` | `2e661bcf790920dcadfe005d282ea6ec1dfe4743` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/factory-validation-robustness-boundary-20261008` | `7173ef08ef90c8ef4f262bdb83ca8d2771cc47f7` | Factory/Candidate Lab | — | REVIEW_REQUIRED |
| `test/github-write-access-20260923` | `64be0c2ec92669b2bf3f4c3db0b04a2e1a91e9f0` | Test/Infrastructure | — | REVIEW_REQUIRED |

## Open PRs and base/head relationships

| PR | Title | Head branch @ SHA | Base branch @ SHA | Draft |
|---:|---|---|---|---|
| #126 | feat: isolated deterministic engine foundation | `dev/deterministic-engine-foundation-clean-2026-09-14` @ `2ba192865a29cc6722ccc28097ffc4ec2af5e715` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #147 | research: establish finite SP2L source-resolution stop condition | `research/sp2l-source-resolution-stop-condition-2026-09-14` @ `b52fc6bc98c349bdaf604fa9b1d1284f5decd9b2` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #149 | research: record direct SP2L source-video frame extraction | `research/sp2l-video-source-extraction-2026-09-14` @ `9c9669e87b9e8ab6531c73ec09af8741332c61d4` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #151 | research: cross-resolve authoritative SP2L transcript | `research/sp2l-transcript-cross-resolution-clean-2026-09-14` @ `825cb4b007ad4b4ad88d0519efaa8db918bd940a` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #155 | research: implement source-safe SP2L synthetic fixture contract | `research/sp2l-synthetic-fixture-contract-2026-09-14` @ `24f3b6301284d34a5cb08786adfb8e66f30f01ce` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #156 | research: establish SP2L frozen-geometry contract | `research/sp2l-frozen-geometry-contract-2026-09-14` @ `8bf4c45b26ac03063c913fba2d33cf4ab9b10d58` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #157 | research: establish SP2L frozen-geometry readiness gate | `research/sp2l-frozen-geometry-readiness-2026-09-14` @ `33bc97e5788f6dfb38c5ecf01df632b423337d15` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #158 | research: add source-safe SP2L replay harness | `research/sp2l-source-safe-replay-2026-09-15` @ `6f20c8aa1e12b1dca0af405a84732f769c5c7932` | `research/sp2l-synthetic-fixture-contract-2026-09-14` @ `24f3b6301284d34a5cb08786adfb8e66f30f01ce` | no |
| #164 | research: assess GitHub Spec Kit adoption for SP2L | `research/sp2l-spec-kit-adoption-2026-09-15` @ `96843f9050f4c9f7857dc006e7d94e440a5ee364` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #165 | engineering: run non-canonical Spec Kit pilot for coverage infrastructure | `research/sp2l-spec-kit-pilot-coverage-2026-09-15` @ `49d87dc0f3885689b61d5f01f0b678e2e8280d21` | `main` @ `f56e73a5f2a38c16245e5bef45a58dbce6c7a8c1` | no |
| #173 | research: record current SP2L project state snapshot | `research/sp2l-current-state-snapshot-2026-09-15` @ `50b05111ff12c23756306365bd1a423630454a3f` | `main` @ `10baa6f37e9729c098b330aa85de6bd5915385b8` | no |
| #176 | research: add SP2L readiness dashboard | `research/sp2l-readiness-dashboard-2026-09-15` @ `ac9f56b82607bebe886b5d5bc4228a933b46f1ec` | `research/sp2l-current-state-snapshot-2026-09-15` @ `50b05111ff12c23756306365bd1a423630454a3f` | no |
| #177 | research: add executable human adjudication worksheet | `research/sp2l-adjudication-worksheet-2026-09-15` @ `277037134d87053d2357e0ecdb37d7b108e57d83` | `research/sp2l-manual-adjudication-gate-2026-09-15` @ `8d14e66e25049be592ca512313e430b282e4268e` | no |
| #184 | engineering: define SP2L research versus MT5 data architecture | `research/sp2l-data-architecture-contract-2026-09-15` @ `bf721f95459b25221a5c3fa2524d07221f11d3cc` | `main` @ `10baa6f37e9729c098b330aa85de6bd5915385b8` | no |
| #185 | research: persist source-video frame audit and SP2L continuity snapshot | `research/sp2l-source-video-frame-audit-2026-09-15` @ `be1afb9bf41f757463af5e91bfaef1351264567b` | `main` @ `10baa6f37e9729c098b330aa85de6bd5915385b8` | no |
| #194 | research: candidate event fixture contract without geometry inference | `research/sp2l-candidate-events-2026-09-15` @ `7137aa19c77421d41dc0f6d91b8138ec0dc8da68` | `main` @ `10baa6f37e9729c098b330aa85de6bd5915385b8` | yes |
| #211 | research: F8 F12 F16 chain forensic evidence | `research/sp2l-f8-f12-f16-chain-forensic-2026-09-16` @ `7c8e53a13cb3788a7402a3c5f28543f387a36de9` | `research/sp2l-primary-artifact-f14-forensic-2026-09-16` @ `13487b4c2ddcce142a4c93918c99fc1f8a1e5cf0` | yes |
| #212 | test: harden SP2L frozen-gate blocker coverage | `research/sp2l-gate-coverage-hardening-2026-09-16` @ `bbacbec17742b37fc6d1f927a23f6404eda031f4` | `research/sp2l-f8-f12-f16-chain-forensic-2026-09-16` @ `7c8e53a13cb3788a7402a3c5f28543f387a36de9` | yes |
| #213 | test: enforce frozen-geometry boundary before canonical backtest | `research/sp2l-canonical-gate-enforcement-2026-09-16` @ `344db899a8d4d41a41f29d85e2ca0aa677cd4f1e` | `research/sp2l-f8-f12-f16-chain-forensic-2026-09-16` @ `7c8e53a13cb3788a7402a3c5f28543f387a36de9` | yes |
| #214 | research: P-Gap source-resolution candidate ledger | `research/sp2l-pgap-source-resolution-2026-09-16` @ `d331f1774b4a32b583757efe3fb163c7b9a4bb0b` | `research/sp2l-f8-f12-f16-chain-forensic-2026-09-16` @ `7c8e53a13cb3788a7402a3c5f28543f387a36de9` | yes |
| #222 | research: primary trigger and order-lifecycle forensic pass | `research/sp2l-trigger-order-lifecycle-forensic-2026-09-16` @ `efa701fac51205d60f2e7200eb98e46b4fe938e5` | `research/sp2l-pgap-source-resolution-2026-09-16` @ `d331f1774b4a32b583757efe3fb163c7b9a4bb0b` | yes |
| #223 | research: worked-trade execution semantics forensic pass | `research/sp2l-worked-trade-forensic-2026-09-16` @ `c237b2e91378f8720549908c0286df3d4d9b47d9` | `research/sp2l-trigger-order-lifecycle-forensic-2026-09-16` @ `efa701fac51205d60f2e7200eb98e46b4fe938e5` | yes |
| #225 | research: worked-trade chart/history timeline reconstruction | `research/sp2l-worked-trade-timeline-forensic-2026-09-16` @ `ddf465603244c0c53cae207cf3e8462f2682874d` | `research/sp2l-worked-trade-forensic-2026-09-16` @ `c237b2e91378f8720549908c0286df3d4d9b47d9` | yes |
| #226 | research: worked-trade entry geometry forensic | `research/sp2l-entry-geometry-forensic-2026-09-16` @ `e9560bc51e659316996b032dfe5570b1de898f5f` | `research/sp2l-worked-trade-timeline-forensic-2026-09-16` @ `ddf465603244c0c53cae207cf3e8462f2682874d` | yes |
| #227 | research: Batch 34 primary SP2L sequence geometry forensic | `research/sp2l-primary-sequence-geometry-forensic-2026-09-17` @ `d7b5b465832de6beb4bc0609326f978d90ce4799` | `research/sp2l-entry-geometry-forensic-2026-09-16` @ `e9560bc51e659316996b032dfe5570b1de898f5f` | yes |
| #228 | research: Batch 35 official-source P-Gap and 2X resolution | `research/sp2l-source-resolution-pgap-2x-2026-09-17` @ `e377695d77aa81141df189a96bc545fe828635c1` | `research/sp2l-primary-sequence-geometry-forensic-2026-09-17` @ `d7b5b465832de6beb4bc0609326f978d90ce4799` | yes |
| #229 | research: Batch36 P-Gap forensic source resolution | `research/sp2l-pgap-forensic-batch36-2026-09-17` @ `539be81dc2a2a5a8eca44a403431738699280bdd` | `research/sp2l-source-resolution-pgap-2x-2026-09-17` @ `e377695d77aa81141df189a96bc545fe828635c1` | yes |
| #230 | research: Batch37 P-Gap mirror/indexing negative-resolution | `research/sp2l-pgap-forensic-batch37-2026-09-17` @ `6b4bb4d18cbee5b50cf4c1885c231bd529bdf421` | `research/sp2l-pgap-forensic-batch36-2026-09-17` @ `539be81dc2a2a5a8eca44a403431738699280bdd` | yes |
| #231 | research: Batch38 author implementation crosswalk | `research/sp2l-author-implementation-crosswalk-batch38-2026-09-17` @ `e8e867be6aec56b3390c4566c2bdd36f8980cf2f` | `research/sp2l-pgap-forensic-batch37-2026-09-17` @ `6b4bb4d18cbee5b50cf4c1885c231bd529bdf421` | yes |
| #232 | research: Batch39 F14 AB=CD primary-video forensic | `research/sp2l-f14-abcd-primary-video-batch39-2026-09-17` @ `7067fe6b99c43fe2737f7a16d07eef54eef162bf` | `research/sp2l-author-implementation-crosswalk-batch38-2026-09-17` @ `453e0b25d0c0016a70d5a38125c02878db83fa89` | yes |
| #233 | research: author replica candidate backtest harness | `research/sp2l-author-replica-backtest-batch40-2026-09-17` @ `b2249e0e1af03646411d728cf8298552960db5cf` | `research/sp2l-f14-abcd-primary-video-batch39-2026-09-17` @ `7067fe6b99c43fe2737f7a16d07eef54eef162bf` | yes |
| #235 | research: prepare guarded live MT5 + Telegram gateway | `research/sp2l-live-mt5-telegram-2026-09-19` @ `22b437fb86600356aa4e315da3a95da200e8500c` | `research/sp2l-mt5-session-matrix-2026-09-17-x` @ `2c3aa5757c74d9e812d6cb1ca6ef690be7f4fd0f` | yes |
| #236 | research: MT5 session matrix, acquisition pipeline, and provenance research | `research/sp2l-mt5-session-matrix-2026-09-17-x` @ `7fd80a93cdad3f25a7b8a02d02603d5208ef5de6` | `main` @ `c5691b23e4f71594a242df5cd4c0375fe69db542` | no |
| #244 | feat: notify Telegram from reconciled MT5 TP SL exits | `research/sp2l-telegram-result-reconciliation-2026-09-21` @ `80d9e906ebad85f2c04da7d2540f9fb09895d27f` | `research/sp2l-telegram-format-implementation-2026-09-21` @ `a01c974e38cb32dd31cc6b1649ab024c4953a767` | yes |
| #251 | Research: Batch46 remaining source blocker closure pass | `research/sp2l-batch46-source-blocker-closure-2026-09-21` @ `c19a0eb2418a1189caf553a9a7d80a4980960744` | `main` @ `c5691b23e4f71594a242df5cd4c0375fe69db542` | yes |
| #252 | research: consolidate remaining source blockers F08-F13 | `research/sp2l-remaining-source-blockers-f08-f13-2026-09-21` @ `8d0e9279f5701e069432f23a4ae0e8a32716dc8b` | `main` @ `c5691b23e4f71594a242df5cd4c0375fe69db542` | yes |
| #254 | research: complete unresolved synthetic fixture gate | `research/sp2l-complete-unresolved-synthetic-fixtures-2026-09-21` @ `690eaf0fa889d8a440b2e4ec8e03dd7de8a8036b` | `research/sp2l-remaining-source-blockers-f08-f13-2026-09-21` @ `8d0e9279f5701e069432f23a4ae0e8a32716dc8b` | no |
| #255 | research: record author-site F13/F12 source evidence | `research/sp2l-author-site-f13-source-update-2026-09-21` @ `c66fcb36dafa3d7f4ea6d97cc6d2a01f465b2c37` | `research/sp2l-complete-unresolved-synthetic-fixtures-2026-09-21` @ `690eaf0fa889d8a440b2e4ec8e03dd7de8a8036b` | no |
| #256 | research: add F13 2X synthetic fixture gate | `research/sp2l-f13-2x-synthetic-fixtures-2026-09-21` @ `d5f308cbf04b6dad3909dc1734bed0377ec65be8` | `research/sp2l-author-site-f13-source-update-2026-09-21` @ `c66fcb36dafa3d7f4ea6d97cc6d2a01f465b2c37` | no |
| #257 | research: reconcile F13 2X source anchors | `research/sp2l-f13-source-reconciliation-2026-09-21` @ `366ad624fff122f6fb197f69ca634154bcf7ea09` | `research/sp2l-f13-2x-synthetic-fixtures-2026-09-21` @ `d5f308cbf04b6dad3909dc1734bed0377ec65be8` | no |
| #260 | research: add P-Gap source reconstruction synthetic fixtures | `research/sp2l-pgap-synthetic-fixtures-2026-09-21` @ `2d8b527b3222e7ad0564b1fef2247d0bacd0309e` | `research/sp2l-pgap-source-reconstruction-2026-09-21` @ `051ac79517501b821daf49d67ef08b9f36f8a7c8` | no |
| #261 | research: extend SP2L source reconstruction with AB=CD discrimination | `research/sp2l-pgap-synthetic-fixtures-2026-09-21` @ `2d8b527b3222e7ad0564b1fef2247d0bacd0309e` | `main` @ `c5691b23e4f71594a242df5cd4c0375fe69db542` | no |
| #263 | research: freeze source boundary and unresolved fixture plan | `research/sp2l-source-boundary-fixture-plan-2026-09-21` @ `cf5fc14f6dc6db3d6f54d051b9a5e7305b0989d6` | `main` @ `1d73a2731d95c3af51a291e1612232cec56b2bdb` | yes |
| #284 | fix(forward): normalize MT5 pending lifecycle collections | `fix/rr2-trail4-pending-lifecycle-tuple-20261008` @ `ef39c3aa5792f26081504504a1066898edfe0bbf` | `research/sp2l-starnet-engine-integration-20261007` @ `575e20453153509cc0c0bc2c70e7aed060681e4b` | no |
| #285 | fix(forward): normalize MT5 pending lifecycle collections | `fix/forward-pending-lifecycle-20261008` @ `76dc9ffec8ddfd1ac642dd49b8fe60bb9d8aa0d8` | `research/sp2l-starnet-engine-integration-20261007` @ `575e20453153509cc0c0bc2c70e7aed060681e4b` | no |
| #287 | feat(factory): add deterministic candidate lab for research optimization | `research/factory-candidate-lab-20261010` @ `cb741ff3768f27ac69923fca7ca3320cea89782c` | `research/sp2l-starnet-engine-integration-20261007` @ `befec09c752e8d7ba9d10ff75d4e39ad5351c853` | yes |
| #288 | fix(forward): make RR2 TRAIL4 pending expiry restart-safe | `fix/rr2-trail4-pending-lifecycle-safe-20261011` @ `c54fce17c5b6014031775812a517fa0c84eae626` | `fix/rr2-trail4-pending-lifecycle-list-20261008` @ `9ed008d01f14c6cde70cc7a569ecf8037360670d` | yes |
| #293 | Add RR2/TRAIL4 market-data availability diagnostics | `fix/rr2-trail4-market-data-diagnostics-20261013` @ `f30b7cbcfa66dad88bc9e6b3ed205a1677191eaa` | `fix/rr2-trail4-pending-lifecycle-safe-20261011` @ `8dd367e9c619110d0b07c6b05888dce631b1f60a` | no |
| #297 | [Research] Audit SP2L entry geometry against previous candle levels | `research/entry-geometry-diagnostic-20261013` @ `0cefdeeaf79bbcc426c456e2f3e2609da0434e1a` | `research/trailing-matrix-audit-20261013` @ `095666a1d3dfa588b635e66e630189a81fc779e3` | yes |
| #302 | fix(telegram): suppress stale MT5 lifecycle deal notifications | `fix/rr2-trail4-stale-telegram-deals-20261014` @ `d2344e571bbb7d87fe11774268477b018a007244` | `fix/rr2-trail4-pending-lifecycle-safe-20261011` @ `c54fce17c5b6014031775812a517fa0c84eae626` | no |
| #306 | Record Factory worker journal audit findings (2026-10-14) | `research/factory-journal-audit-snapshot-20261014` @ `a9c5a567399b39225f6b6e2aad1147b4c75a2295` | `research/xauusd-availability-integrity-gate-20261013` @ `a6598aca2f559f813829681e5f2eeedfdcbd8657` | yes |
| #315 | Research: compare current RR2/TRAIL4, London-to-NY, and no trailing | `research/rr2-trail4-session-vs-no-trailing-20261015` @ `c14d96b3d2c65dc04e7e2741aba9dfbad6f8c9c6` | `fix/rr2-trail4-telegram-deal-time-20261013` @ `d4e02164256872fe4bd240d66bdc3197e17f0fe3` | yes |
| #323 | Fix CRLF normalization byte escapes in raw M1 audit | `fix/factory-raw-m1-normalization-escape-20261015` @ `ff1c106d03ae94092f79788038f7c2a0364dc645` | `research/factory-candidate-lab-20261010` @ `cb741ff3768f27ac69923fca7ca3320cea89782c` | no |
| #327 | docs: establish safe branch governance and archive plan | `chore/branch-governance-inventory-20261015` @ `2add432a5c732629cdecc8bcf2673884c19d5da6` | `main` @ `6ac7db6ffa5101b42adfb96ece16674c4e9130bf` | yes |

## Archive decision gate

A branch must not be archived/deleted until all are true:
- its full commit range versus the relevant reference is inspected;
- it has no unique commit, code, research result, fixture, audit artifact, snapshot, or runtime evidence that is not preserved elsewhere;
- no open PR, dependent branch, workflow, or local worktree depends on it;
- a recovery ref/tag or immutable SHA is recorded and verified;
- any local dirty/untracked work is separately protected;
- deletion candidates are reviewed as a small batch before execution.

### Current recommendation

Do not delete any branch based on this inventory alone. The large chain of open source-research PRs and forward fixes shows branch ancestry and PR dependencies are material. First map the dependency chains, then identify completed chains whose content is already preserved on a verified base. Keep Factory, Backtest/Validation, and Forward operationally separate.

### Local-only work limitation

This report inventories GitHub remote refs only. It does not inspect Windows local branches, dirty worktrees, untracked evidence, running PS1/PS2 processes, or MT5 state. In particular, local branch `fix/rr2-trail4-pending-lifecycle-list-local-20261008` was previously reported as local-only and must be checked on the user's machine before any cleanup.
