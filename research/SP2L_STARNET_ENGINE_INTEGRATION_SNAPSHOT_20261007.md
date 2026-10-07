# SP2L Strategy Research Factory — StarNet Integration Snapshot 2026-10-07

## Snapshot identity

- Branch: `research/sp2l-starnet-engine-integration-20261007`
- Integration purpose: StarNet-derived world-engine spike for the SP2L Research Factory UI.
- Upstream engine repository: `androoAGI/starnet`
- Pinned upstream commit: `e0a36dcd31787248b877aea01a6e53741012bc46`
- Bootstrap: `scripts/bootstrap_starnet_engine.ps1`
- Local vendor path: `vendor/starnet-engine`
- Vendor state at snapshot: clean, detached at the pinned commit.
- Strategy A geometry: unchanged.
- Active MT5 forward runner: unchanged.
- Production BUY/SELL authority: locked.

## Why this branch exists

The existing Factory dashboard proved telemetry-backed workers, queue lifecycle, evidence artifacts, and research-only governance. Its hand-authored station world is useful as a prototype but does not attempt to reproduce a mature world engine.

This branch evaluates a safer architecture:

```
StarNet-derived world infrastructure
        ↓
SP2L world adapter / contract
        ↓
Factory telemetry + queue + evidence
        ↓
Research Station presentation
```

The Factory remains the source of truth for research state. The world engine is a presentation/runtime substrate and must not become a strategy engine.

## Upstream inspection boundary

The StarNet source was inspected at the pinned commit. Relevant engine areas include:

- `frontend/app/world.js` — live station rendering, camera, agent movement/pathing and world presentation.
- `frontend/app/worldmodel.js` — station/world model and geometry/path representation.
- `frontend/app/stationbake.js` — generalized station bake/render pipeline.
- `frontend/app/app.js` — frontend state/runtime integration.
- `shared/events.js` — upstream event contract.
- `frontend/app/BUILDER.md` — world/model extension guidance.

The integration does **not** copy StarNet's brand identity, logo, station artwork, or sprites as canonical SP2L identity.

## SP2L ownership boundary

SP2L owns:

- research job identity;
- worker/job telemetry;
- station/phase assignment;
- queue lifecycle;
- evidence/artifact identity;
- research governance;
- production lock;
- SP2L branding and artwork;
- the adapter contract connecting Factory truth to the world engine.

StarNet-derived infrastructure may provide:

- canvas/world rendering infrastructure;
- camera and viewport mechanics;
- generic room/corridor representation;
- generic pathing primitives;
- generic body/animation infrastructure.

The adapter must not:

- generate Strategy A signals;
- define P-Gap geometry;
- resolve source ambiguity;
- optimize candidates;
- create production BUY/SELL decisions;
- invent worker activity;
- turn decorative animation into research telemetry.

## Telemetry truth rule

Only `runtime/factory_worker_status.json` and the Factory queue/job contracts may drive visible worker/job state.

A worker may appear active only when telemetry says it is active.

A job may move through Queue → Lab → Evidence → Complete only from actual Factory lifecycle state.

The world layer may animate a real worker, but animation timing is presentation only and cannot create or alter research state.

## Current Strategy A safety state

Source resolution remains active.

Frozen geometry remains blocked.

Unresolved items remain unresolved, including executable P-Gap construction, F12 interaction/fill semantics, exact F10 SL anchor, C06 pending lifetime, AB=CD anchors/tolerance, TP formulas and other source-gated semantics.

Therefore this integration branch cannot create a canonical Strategy A engine.

## Verification plan

1. Bootstrap and pin the upstream engine.
2. Freeze this integration snapshot.
3. Implement a minimal SP2L world adapter that translates Factory telemetry into a deterministic world-state contract.
4. Unit-test the adapter without importing or executing Strategy A logic.
5. Add the adapter to the dashboard only after the contract tests pass.
6. Keep the existing hand-authored world as fallback until the new engine path is verified.
7. Validate worker containment, pacing, queue flow, and telemetry truth.
8. Do not modify the live forward runner.

## License / identity boundary

StarNet code is MIT-licensed at the pinned revision. StarNet's own name, logo, station artwork, sprites, and brand identity are explicitly excluded from that code license according to its upstream notice.

SP2L therefore uses the upstream code as an implementation reference/vendor source while retaining an independent SP2L name, logo, artwork, and research identity.

## Non-goals

- No Strategy A rule invention.
- No live execution integration.
- No MT5 order generation.
- No fake telemetry.
- No simulated research results.
- No production authorization.
- No mass cleanup of existing local forward-test artifacts.

## Immediate next milestone

**SP2L World Adapter v0.1**

Input:
`FactoryWorker.as_dict()` / normalized worker telemetry.

Output:
A deterministic, renderer-neutral station state describing real workers, their station, lifecycle state, progress, and optional artifact identity.

The adapter is intentionally independent of StarNet's frontend code so the research contract can be tested before any renderer is connected.


## Integration Spike v0.2 — 2026-10-07

- Dashboard world now consumes `src/strategy_factory/starnet_adapter.py`.
- Worker ordering is deterministic by `worker_id`.
- World station assignment comes from validated Factory telemetry rather than inferred decorative state.
- Dashboard identity now displays **CEO: Ali** / **COMMAND: CEO ALI**.
- No worker/job activity is fabricated by the identity layer.
- Production remains locked and BUY/SELL generation remains zero.
- The existing live forward runner and Strategy A geometry remain untouched.

This is still a renderer integration spike, not a Strategy A execution engine. The pinned StarNet source remains isolated under `vendor/starnet-engine`; the next renderer step must consume the same validated world contract rather than bypassing Factory telemetry.
