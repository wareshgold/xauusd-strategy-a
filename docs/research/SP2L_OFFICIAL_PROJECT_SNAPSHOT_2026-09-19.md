# SP2L Official Project Snapshot — 2026-09-19

## Purpose

Permanent resume point for the SP2L / XAUUSD Strategy A project. This snapshot is the authoritative navigation record for the current work state so future sessions resume from here without re-searching prior work or requesting already-archived source evidence.

## Current branch

- Branch: `research/sp2l-live-mt5-telegram-2026-09-19`
- Remote: `origin`
- Current work area: source-resolution research, robustness/stability validation, frozen fresh-holdout readiness, and guarded Nexora MT5/Telegram infrastructure.

## Current gate state

- Frozen Geometry: **BLOCKED**
- Parameter robustness evidence: **POSITIVE**
- Parameter Stability Gate: **INCONCLUSIVE — NO PASS / NO FAIL**
- Fresh Holdout: **WAITING FOR ELIGIBLE POST-BOUNDARY DATA**
- Production/live trading authorization: **BLOCKED**
- Live Trading: **DISABLED**
- Nexora runtime dry-run verification: **PASS**
- Canonicalization firewall: **NO LEAKAGE IDENTIFIED**

Workflow remains:

`SOURCE RESOLUTION → SYNTHETIC FIXTURES → FROZEN GEOMETRY → DEV → UNTOUCHED VALIDATION → ROBUSTNESS/STABILITY → FRESH HOLDOUT → PRODUCTION`

## Latest official research position

### Source / Frozen Geometry audit

Audit:
`docs/research/SP2L_SOURCE_FROZEN_GEOMETRY_AUDIT_2026-09-19.md`

Commit: `5498221df75a9e692aa0f861992ed45109169c80`

Current executable source-confirmation status:

- Executable `SOURCE_CONFIRMED` fields: **0/7**
- Entry: PARTIAL
- Invalidation/SL: PARTIAL
- Limit refresh: PARTIAL
- Trigger: PARTIAL
- 2X: PARTIAL
- AB=CD: PARTIAL
- P-Gap: **UNRESOLVED**

Recent evidence strengthens the source concepts and structural relationships but does not uniquely determine executable geometry. Do not invent P-Gap indexing/boundary semantics, AB=CD A/B/C/D anchors, tolerance, fill semantics, or Leg1=Leg2 equality.

**Frozen Geometry remains BLOCKED.**

### Canonicalization Firewall

Audit:
`docs/research/SP2L_CANONICALIZATION_FIREWALL_AUDIT_2026-09-19.md`

Commit: `664a837a488fb6087664c7786c3e7e215d693d14`

Result: **NO CANONICALIZATION LEAKAGE IDENTIFIED**.

The author-replica runner contains concrete candidate P-Gap/entry/SL expressions for research only. The frozen holdout runner keeps parameters fixed and records integrity flags preventing tuning, source reinterpretation, geometry changes, or fill-semantic changes. The live gateway is an execution boundary and does not calculate Strategy A geometry.

Any future promotion of research expressions into canonical Strategy A requires explicit source-resolution review and Frozen Geometry promotion.

### F14 / AB=CD — next research target

Next step is **F14 AB=CD anchor resolution**:

1. Re-check the primary transcript and Batch34/35 evidence for explicit A/B/C/D endpoint mapping.
2. Determine whether the source uniquely defines the four endpoints.
3. Determine whether any AB=CD tolerance is source-confirmed.
4. If not uniquely resolved, preserve AB=CD as **PARTIAL/UNRESOLVED**.
5. Do not invent pivot rules, `fill=C`, endpoint substitutions, or tolerance from backtest performance.

If F14 cannot be closed, move to the next source-resolution blocker (pending-order lifecycle / invalidation-SL evidence) rather than running another backtest.

## Parameter Robustness

81-combination bounded matrix:

- P-Gap: 0.8 / 1.0 / 1.2
- Spike Multiplier: 1.3 / 1.5 / 1.7
- Max SL: 8 / 10 / 12
- TP: 0.8 / 1.0 / 1.2R

Baseline:

- 158 signals
- 103 wins / 51 losses / 4 ambiguous
- 66.883% decisive WR
- +52R
- PF 2.02

Full matrix:

- 81/81 positive Total R
- 80/81 above 60% decisive WR
- mean decisive WR 65.733%
- median decisive WR 65.972%
- min decisive WR 59.794%
- max decisive WR 70.968%

This is research evidence only; no parameter is promoted to canonical status.

Robustness analysis:
`docs/research/SP2L_PARAMETER_ROBUSTNESS_ANALYSIS_2026-09-19.md`

## Parameter Stability

Protocol:
`docs/research/SP2L_PARAMETER_STABILITY_PROTOCOL_2026-09-19.md`

Protocol commit: `a6b8ad174306ace0118d2344501c129951a240d0`

Assessment commit: `d69f58ab1886dbe19f092c824544dd8257dd13c0`

Assessment: **INCONCLUSIVE — NO PASS / NO FAIL**

- S1 surface concentration: POSITIVE
- S2 baseline locality: POSITIVE
- S3 temporal consistency: MIXED / INCONCLUSIVE
- S4 main effects: COMPLETE / DESCRIPTIVE
- S5 multiple-testing guard: PASS
- S6 uncertainty: DESCRIPTIVE / LIMITED

No parameter promotion follows from this assessment.

## Fresh Holdout

Frozen boundary: **2026-09-19 00:00:00 UTC**

Latest availability check returned:

- `HOLDOUT_DATA_UNAVAILABLE`
- 0 post-boundary XAUUSD.ecn M1 bars
- no reported MT5 acquisition error
- returned history did not cross the frozen boundary

Because 2026-09-19 was Saturday, this is consistent with observed market-data availability. It is not a strategy result and is not a failed holdout.

Frozen configuration:

- XAUUSD.ecn / M1
- P-Gap 1.0
- Spike Multiplier 1.5
- Max SL 10
- TP 1.0R

Do not substitute pre-boundary data. Rerun only after eligible post-boundary data exists.

Runner:
`scripts/run-author-replica-mt5-fresh-holdout.py`

Availability audit:
`docs/research/SP2L_FRESH_HOLDOUT_MT5_DATA_AVAILABILITY_2026-09-19.md`

Integrity audit:
`docs/research/SP2L_FRESH_HOLDOUT_INTEGRITY_AUDIT_2026-09-19.md`

## Nexora MT5 + Telegram Infrastructure

Existing guarded live infrastructure is already implemented. Do **not** rebuild it from scratch.

Authoritative gateway:
`scripts/live_mt5_gateway.py`

Safety:

- `LIVE_TRADING_ENABLE=false`
- execution requires explicit external APPROVED signal
- gateway does not calculate Strategy A geometry
- MAX_OPEN_POSITIONS guard remains active
- duplicate signal rejection is implemented
- public Telegram branding is **Nexora SIGNAL / Nexora EXECUTION**
- internal broker comment may remain `SP2L:<signal_id>`

Runtime verification:
`docs/research/NEXORA_RUNTIME_VERIFICATION_CHECKPOINT_2026-09-19.md`

Verification result:

- signal archive: PASS
- signal journal: PASS
- trade journal: PASS
- Excel export: PASS
- broker reconciliation: PASS
- `LIVE_TRADING_ENABLE=false`
- no real order / no MT5 deal / no production Strategy A signal

## Future Nexora VIP Client Roadmap

Recorded for later, intentionally non-operational:

`docs/research/NEXORA_VIP_CLIENT_ARCHITECTURE_ROADMAP_2026-09-19.md`

Planned layers:

1. Installer / Client Shell
2. Release / Update Manager
3. VIP Authorization
4. MT5 Discovery / Connection Adapter
5. Strategy Runtime Boundary
6. Existing Guarded Execution Gateway
7. Observability / Support

No installer, auto-update, VIP authentication, or automated live-order path is operationalized by this roadmap.

## Resume Instructions

When continuing:

1. Start from this snapshot and the current branch.
2. Do not re-request the original source video.
3. Do not rebuild the existing live infrastructure.
4. Keep live execution disabled.
5. Continue source-resolution research first; next target is F14 AB=CD anchors/tolerance.
6. Do not use backtest/robustness performance to invent unresolved source geometry.
7. Run the frozen Fresh Holdout only after eligible post-2026-09-19 data exists.
8. Do not substitute pre-boundary data.
9. Do not authorize production trading while Frozen Geometry is BLOCKED.

## Official snapshot history

- `76259bce078678e3d0f2a3c083ef18d021300e78` — latest prior official snapshot / canonicalization firewall registration.
- This update records the current resume point for the next chat, including the explicit F14 AB=CD next step and current gate states.
