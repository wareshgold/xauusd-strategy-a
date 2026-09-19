# SP2L Official Project Snapshot — 2026-09-19

## Purpose

Permanent resume point for the SP2L / XAUUSD Strategy A project. This snapshot is the authoritative navigation record for the current work state so future sessions resume from here without re-searching prior work or requesting already-archived source evidence.

## Current branch

- Branch: `research/sp2l-live-mt5-telegram-2026-09-19`
- Remote: `origin`
- Current work area: live MT5 + Telegram infrastructure alongside research/validation gates.

## Strategy research state

Workflow remains:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

Current gate state:

- Frozen Geometry: **BLOCKED**
- Parameter robustness evidence: **POSITIVE**
- Parameter Stability Gate: **INCONCLUSIVE — NO PASS / NO FAIL**
- Fresh Holdout: **NOT RUN / NO ELIGIBLE POST-BOUNDARY BARS YET**
- Production/live trading authorization: **BLOCKED**

### Robustness snapshot

81-combination bounded matrix completed for:
- P-Gap: 0.8 / 1.0 / 1.2
- Spike Multiplier: 1.3 / 1.5 / 1.7
- Max SL: 8 / 10 / 12
- TP: 0.8 / 1.0 / 1.2R

Baseline:
- P-Gap 1.0
- Spike Multiplier 1.5
- Max SL 10
- TP 1.0R
- 158 signals
- 103 wins / 51 losses / 4 ambiguous
- 66.883% decisive win rate
- +52R
- PF 2.02

Full matrix:
- 81/81 combinations positive Total R
- 80/81 above 60% decisive WR
- mean decisive WR 65.733%
- median decisive WR 65.972%
- min decisive WR 59.794%
- max decisive WR 70.968%

Do not promote the best-performing parameter combination to canonical status. Matrix is research evidence only.

### Parameter Stability

A pre-registered stability protocol was added at `docs/research/SP2L_PARAMETER_STABILITY_PROTOCOL_2026-09-19.md`.

It formalizes surface concentration, baseline locality, temporal consistency, parameter main-effect sensitivity, multiple-testing protection, and descriptive statistical uncertainty. It does not select or promote a canonical parameter and does not alter strategy geometry.

Protocol commit: `a6b8ad174306ace0118d2344501c129951a240d0`.

Assessment commit: `d69f58ab1886dbe19f092c824544dd8257dd13c0`.

S4 complete: direct 81-row raw-matrix main effects computed for P-Gap, Spike Multiplier, Max SL, and TP.

S1 surface concentration: positive. S2 baseline locality: positive. S3 temporal consistency: mixed/inconclusive. S4 main-effect aggregation: complete / descriptive. S5 multiple-testing guard: pass. S6 uncertainty: descriptive/limited.

## Fresh Holdout

Frozen boundary: **2026-09-19 00:00:00 UTC**.

A new untouched availability check was executed on 2026-09-19 through 07:37 UTC. The committed single-configuration runner requested post-boundary XAUUSD.ecn M1 data and returned:

- `HOLDOUT_DATA_UNAVAILABLE`
- 0 returned bars
- no reported MT5 acquisition error

Earlier `copy_rates_from` diagnostics also showed returned history ending at **2026-09-18 23:57 UTC**, so no returned sample has crossed the frozen boundary.

Because 2026-09-19 is Saturday, this is consistent with observed market-data availability. It is **not** a strategy result and does not count as a failed holdout.

Earlier data must not be substituted.

Frozen holdout configuration:
- XAUUSD.ecn
- M1
- P-Gap 1.0
- Spike Multiplier 1.5
- Max SL 10
- TP 1.0R

No holdout tuning, subperiod selection, geometry reinterpretation, fill-rule changes, or source reinterpretation.

Availability diagnostic: `docs/research/SP2L_FRESH_HOLDOUT_MT5_DATA_AVAILABILITY_2026-09-19.md`.

## Live MT5 + Telegram infrastructure

The project already had an existing guarded live implementation (PR #235 / checkpoint `c3b97ae62068216020b766a4acfc67c6b8667d9e`). Do **not** restart or rebuild this subsystem from scratch.

Existing verified scope:
- MT5 connectivity
- XAUUSD.ecn
- explicit APPROVED signal contract
- dry-run execution
- Telegram echo
- append-only JSONL journal
- Excel export: `runtime/exports/SP2L_Live_Trade_Journal.xlsx`
- broker-side reconciliation
- duplicate signal protection
- market/account snapshots

Safety state:
- `LIVE_TRADING_ENABLE=false` by default
- Strategy A signal generation is intentionally separate from execution
- Gateway does not define or alter P-Gap / AB=CD / Leg1=Leg2 / fill semantics

### Recent live-infrastructure changes

- Removed redundant duplicate gateway implementation `scripts/mt5_live_gateway.py`.
- Authoritative gateway remains `scripts/live_mt5_gateway.py`.
- Duplicate signal rejection now:
  - records `DUPLICATE_REJECTED` in the signal journal;
  - records the rejection reason;
  - emits Telegram acknowledgement;
  - archives the consumed signal file.

Added offline safety tests in:
`tests/test_live_mt5_gateway.py`

Coverage:
1. non-APPROVED signal rejection;
2. SELL dry-run order construction using bid;
3. MAX_OPEN_POSITIONS guard.

Runtime verification checkpoint completed on 2026-09-19:
- synthetic dry-run signal archive: PASS;
- signal journal: PASS;
- trade journal: PASS;
- Excel export: PASS;
- broker reconciliation: PASS (signals=5, mt5_deals=0, matched_signals=0, newly_recorded_closed=0);
- public Telegram branding verified as Nexora SIGNAL / Nexora EXECUTION;
- LIVE_TRADING_ENABLE=false throughout the test.

Checkpoint: `docs/research/NEXORA_RUNTIME_VERIFICATION_CHECKPOINT_2026-09-19.md` (commit `dad25b2537b4da21f74adca13bde6340cb9e3fef`).

No real trade was enabled or authorized by this verification.

## Important archived evidence / gates

- Visual Artifact Acquisition Gate: commit `67fb8a2847daf973e8df83224a9074fce9ab0df3`
- Frozen Geometry TypeScript CI fix: `612820dc3c3dce102ff5fb710045abe7b51b40d6`
- Robustness matrix archive: `0810a26`
- Robustness analysis: `f4de3f6bd8490a8fe08dc47f66d83f64b358f3d2`
- Fresh Holdout boundary freeze: `b9324eb0bc5231f0b64e8347c1451c2267b3b778`
- Fresh Holdout runner: `08f2fc01fb4ac92e1cc38545164433a24242ffd6`
- Weekend holdout availability audit: `e096283315d3394f56986cac1b5cf4d25e195506`
- Fresh Holdout integrity audit: `410a69da38f7d846ba59035aca9f764fe144db4c`
- Live infrastructure audit: `d50893ac759ec6b5daf806730fe5ae82c99d07f3`
- Live gateway safety tests: `87166f75d97be283f002277b22550df2f0a5ff0d`
- Live gateway journal duplicate fix: `aef1041aab5c43c79b09b6d491f1b19dd3ebca95`

## Resume instructions

When continuing this project:
1. Start from this snapshot and the current branch.
2. Do not re-request the original source video or redo already archived source resolution.
3. Do not rebuild PR #235 live infrastructure.
4. Keep live execution disabled.
5. Continue the frozen Fresh Holdout only after eligible post-2026-09-19 data exists.
6. Do not substitute pre-boundary data.
7. Do not use backtest/robustness performance to invent unresolved source geometry or authorize production trading.

## Combined Readiness Audit — 2026-09-19

A non-invasive combined audit was completed across Parameter Stability, execution infrastructure, and the Source/Frozen Geometry gate.

- Parameter Stability: **INCONCLUSIVE — NO PASS / NO FAIL**
- Execution infrastructure: **READY / GUARDED** for controlled dry-run; not authorization for Strategy A production auto-signals.
- Source/Frozen Geometry: **BLOCKED**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Live execution: **DISABLED**

Audit file: `docs/research/SP2L_COMBINED_READINESS_AUDIT_2026-09-19.md`
Audit commit: `94f56b62baf27773c7b56130f308dc836afed6a2`

## Source / Frozen Geometry Gate Audit — 2026-09-19

A fresh repository-level audit was completed after reviewing the current source-evidence ledger and the latest P-Gap / 2X / sequence-forensic batches.

Audit file: `docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`

Audit commit: `5498221df75a9e692aa0f861992ed45109169c80`

Key result:

- Executable `SOURCE_CONFIRMED` fields: **0/7**
- Entry: PARTIAL
- Invalidation/SL: PARTIAL
- Limit refresh: PARTIAL
- Trigger: PARTIAL
- 2X: PARTIAL
- AB=CD: PARTIAL
- P-Gap: **UNRESOLVED**

Recent evidence materially strengthens source concepts and structural relationships, but does not uniquely determine the executable geometry required by the freeze contract. In particular, the latest P-Gap forensic batches still do not resolve current-SP2L indexing, bearish mirror, boundary semantics, threshold/tolerance, or qualifying-candle relation.

The current GitHub tree does not expose the previously referenced `SP2L/Source_Archive/2026-09-17_Original_Video_Visual_Evidence` directory by that exact path. This is recorded only as a repository-storage/path observation; it is not treated as source-evidence loss because the primary-artifact/source-resolution ledger remains present.

**Frozen Geometry remains BLOCKED. No downstream gate is unlocked by this audit.**

## Current operational conclusion

**The infrastructure path is materially implemented and guarded. Parameter Stability remains INCONCLUSIVE — NO PASS / NO FAIL because temporal stability is mixed/inconclusive despite completion of the full S4 main-effect calculation. The untouched Fresh Holdout remains blocked only by lack of eligible post-boundary MT5 data; the latest availability check returned zero bars through 07:37 UTC on Saturday 2026-09-19. The frozen runner integrity path has been audited and remains ready without parameter, geometry, or fill-rule changes. Strategy production remains BLOCKED. The Nexora runtime verification is PASS for the tested dry-run path, and live execution stays disabled.**


## Future Nexora VIP Client / Installer Roadmap — 2026-09-19

A future non-operational product architecture has been recorded for a Nexora Windows client intended for VIP distribution.

Planned layers:
1. Installer / Client Shell
2. Release / Update Manager
3. VIP Authorization
4. MT5 Discovery / Connection Adapter
5. Strategy Runtime Boundary
6. Existing Guarded Execution Gateway
7. Observability / Support

Design constraints:
- GitHub main/release is a versioned source/release input, not unconditional trading authority.
- VIP authorization grants access to an approved release; it does not define Strategy A rules.
- MT5 remains the local broker/data connection.
- The existing guarded execution gateway remains the order boundary.
- No client, installer, auto-update, VIP authentication, or automated live-order path is operationalized by this roadmap.
- No unresolved P-Gap geometry, AB=CD anchors/tolerance, fill semantics, or Leg1=Leg2 rule may be invented or promoted by the future client.

Architecture roadmap: docs/research/NEXORA_VIP_CLIENT_ARCHITECTURE_ROADMAP_2026-09-19.md
Architecture documentation commit: 2f867d744c9eb0fb108b6ac128cf3c34b42cfa7c

The roadmap is intentionally parked until the research gates permit production. Current gates remain unchanged:
- Frozen Geometry: **BLOCKED**
- Parameter Stability: **INCONCLUSIVE — NO PASS / NO FAIL**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Live Trading: **DISABLED**
