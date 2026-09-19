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

S1 surface concentration: positive. S2 baseline locality: positive. S3 temporal consistency: mixed/inconclusive. S4 main-effect aggregation: pending direct raw-matrix computation. S5 multiple-testing guard: pass. S6 uncertainty: descriptive/limited.

## Fresh Holdout

Frozen boundary: **2026-09-19 00:00:00 UTC**.

The first holdout acquisition attempt returned zero bars because 2026-09-19 was Saturday. A `copy_rates_from` diagnostic returned historical data only through 2026-09-18 23:57 UTC. Earlier data must not be substituted into the holdout.

Next valid holdout action: rerun the same frozen single-configuration runner after new post-boundary XAUUSD.ecn M1 data exists.

Frozen holdout configuration:
- XAUUSD.ecn
- M1
- P-Gap 1.0
- Spike Multiplier 1.5
- Max SL 10
- TP 1.0R

No holdout tuning, subperiod selection, geometry reinterpretation, fill-rule changes, or source reinterpretation.

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

Runtime verification still pending:
- restart persistence on local MT5 runtime;
- credentialed Telegram delivery;
- broker-history reconciliation against actual MT5 activity.

No real trade was enabled or authorized by these changes.

## Important archived evidence / gates

- Visual Artifact Acquisition Gate: commit `67fb8a2847daf973e8df83224a9074fce9ab0df3`
- Frozen Geometry TypeScript CI fix: `612820dc3c3dce102ff5fb710045abe7b51b40d6`
- Robustness matrix archive: `0810a26`
- Robustness analysis: `f4de3f6bd8490a8fe08dc47f66d83f64b358f3d2`
- Fresh Holdout boundary freeze: `b9324eb0bc5231f0b64e8347c1451c2267b3b778`
- Fresh Holdout runner: `08f2fc01fb4ac92e1cc38545164433a24242ffd6`
- Weekend holdout availability audit: `385e893f18462a77e431baeb7a48793422251ab8`
- Live infrastructure audit: `d50893ac759ec6b5daf806730fe5ae82c99d07f3`
- Live gateway safety tests: `87166f75d97be283f002277b22550df2f0a5ff0d`
- Live gateway journal duplicate fix: `aef1041aab5c43c79b09b6d491f1b19dd3ebca95`

## Resume instructions

When continuing this project:
1. Start from this snapshot and the current branch.
2. Do not re-request the original source video or redo already archived source resolution.
3. Do not rebuild PR #235 live infrastructure.
4. Keep live execution disabled.
5. Continue pending live-runtime verification only where needed.
6. Separately continue the frozen Fresh Holdout once eligible post-2026-09-19 data exists.
7. Do not use backtest/robustness performance to invent unresolved source geometry or authorize production trading.

## Current operational conclusion

**The infrastructure path is materially implemented and guarded. Parameter Stability has been assessed as INCONCLUSIVE/PENDING only because temporal stability remains mixed/inconclusive despite completion of the full S4 main-effect calculation. Strategy production remains BLOCKED. After S4 completion, the next strategic evidence gate remains the untouched Fresh Holdout using the frozen configuration and boundary once eligible post-boundary data exists; infrastructure runtime verification remains separate and live execution stays disabled.**
