# G416 — Visual Artifact Acquisition Gate

Date: 2026-09-14
Parent: G415 / G410
Status: BLOCKED_PENDING_SOURCE_FRAME_ARTIFACTS

## Purpose

G416 is the controlled handoff from transcript/source-language reconciliation to coordinate-level visual reconciliation. It records exactly what evidence is still required before any executable geometry can be frozen.

This gate does not infer geometry from OHLC data, trading conventions, existing backtest code, or visual similarity described in earlier audit documents.

## Evidence state

The source transcript is available and has materially narrowed the questions. G415 establishes that the source demonstrates a pending-limit order that can be moved or replaced as subsequent candles change the scenario, and that the worked example can measure Leg 1 from a deeper structural origin rather than simply from the eventual fill.

The repository also contains immutable frame identifiers/hashes from earlier source-video audits. However, those identifiers are evidence references, not coordinate-level frame artifacts. G410 explicitly requires the decoded image artifact and its provenance before claiming reproducible extraction.

A File Library search in the current research pass did not surface the requested F3859/F3868/F3869/F3870/F3872 image artifacts or an equivalent complete source-frame bundle. Therefore this gate does not claim that visual extraction has been completed.

## Required visual resolutions

### V1 — P-Gap
Window: 34:14–35:50

Determine only from the source visual:
- the candle(s) defining the displayed P-Gap;
- the relevant boundary/price field(s);
- whether the displayed separation is the executable condition or only an illustration;
- whether both event orderings use the same geometric construction.

Must remain unresolved if the visual cannot uniquely answer these questions.

### V2 — AB=CD anchors
Window: 36:15–37:10

Determine:
- visual A, B, C and D locations;
- whether anchors attach to candle high/low/body/open/close or another source-defined point;
- whether the drawn AB=CD relation uses the same anchor semantics throughout.

No generic swing/pivot algorithm may substitute for the source visual.

### V3 — Entry order
Window: 38:18–40:16

Determine:
- initial Buy Limit reference level;
- relation to the first low;
- whether the order is placed at a boundary or offset;
- update versus replacement semantics;
- cancellation/invalidation boundary before activation.

Fill price must not be equated with C unless directly supported by the visual evidence.

### V4 — Stop and targets
Window: 41:18–42:48

Determine:
- exact structural stop boundary;
- wick/body/OHLC field if visibly identifiable;
- TP1 and TP2 geometric locations;
- whether TP1 is directly tied to R=1 from the displayed entry/stop or mapped another way.

The source-supported R=1 convention does not by itself freeze the price geometry.

### V5 — Deep-leg worked example
Window: 1:04:00–1:04:42

Reconcile:
- lower-high sequence;
- deep structural origin;
- successive order positions;
- activation/fill;
- displayed Leg 1 measurement;
- R=1 and R=2 target references.

This window is particularly important because it can discriminate `Leg1-from-structural-origin` from `Leg1-from-fill`.

## Required artifact schema

For every resolved visual claim record:

- source asset SHA-256;
- requested timestamp;
- actual decoded frame index;
- FPS;
- extraction tool/version;
- output image SHA-256;
- source byte size when available;
- reproducible extraction method;
- visual observation;
- confidence;
- blocker affected;
- resolution status;
- reviewer note if ambiguity remains.

## Fail-closed decision rules

The following remain prohibited until directly source-resolved:

- generic three-candle P-Gap;
- arbitrary wick/body selection;
- arbitrary A/B/C/D pivot selector;
- fill = C;
- invented AB=CD tolerance;
- fixed entry offset chosen for backtest performance;
- stop buffer chosen by convention;
- arbitrary TP2 extension.

A successful backtest cannot change any of these dispositions.

## Gate result

`G416 = BLOCKED_PENDING_SOURCE_FRAME_ARTIFACTS`

`G400 = BLOCKED`

`FROZEN_GEOMETRY = NOT AUTHORIZED`

`DEV = NOT AUTHORIZED`

`VALIDATION = PROTECTED`

`PRODUCTION = BLOCKED`

## Next action

Provide or expose the provenance-controlled decoded frame bundle for the five windows above, preferably including the previously registered frames around 1:04:19–1:04:32. Once the artifacts are available, perform coordinate-level visual reconciliation and only then decide whether any G400 blocker can be closed.
