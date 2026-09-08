# SP2L Project Snapshot — 2026-09-08

## Purpose

Handoff snapshot for continuing the XAUUSD Strategy A / SP2L research in a new chat without re-asking for the source video or source transcript.

## Repository / branch

- Repository: `wareshgold/xauusd-strategy-a`
- Active research branch: `research/sp2l-semantic-contract-freeze-2026-09-08-v2`
- Current branch head at snapshot: `a1d7a133bc96d83f7860df87d2cedf3536056dcb`
- Main must remain untouched.

## Authoritative source artifacts — DO NOT ASK USER TO RE-UPLOAD

### Source video

- Local source path: `/mnt/data/strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: ~4155.72 s (69:15.7)
- FPS: 30
- Frames: 124,670
- Resolution: 640x360
- Video: H264
- Audio: AAC 44.1 kHz stereo
- No embedded subtitle stream was found by ffprobe.
- SHA256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

### Canonical source transcript / treasure map

- Repository path: `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
- SHA256: `47f867385338738a23d2b06dc48e67b852127243`
- Registry: `docs/source/treasure_path/SP2L_SOURCE_TRANSCRIPT_REGISTRY_2026-09-08.md`
- Registry blob SHA: `d0ebeba7cd47861ec444ab7e8574d27fa2b78ffb`

The source video + transcript above are the primary source material. They are already available and have been inspected. A new chat should continue from these artifacts rather than asking for them again.

## Source-confirmed semantic contract

`SPIKE -> P-GAP-valid breakout context -> CORRECTION -> relevant prior Low/High -> PENDING LIMIT -> structural invalidation behind Spike-origin -> SECOND LEG with AB=CD / approximately equal Leg-1 magnitude.`

Strong source evidence also establishes:

- Spike = strong/sharp directional movement after range/context.
- Breakout is associated with follow-through/key-bar behavior.
- Valid Spike requires P-Gap in the source framework.
- Source examples show P-Gap/non-overlap visually, but exact OHLC formula is not frozen.
- Bullish correction reaches prior/relevant Low; bearish correction reaches prior/relevant High.
- Entry is a pending limit that may be placed during correction; no mandatory later market-close reclaim is canonical.
- Source allows pending-order deletion/replacement if stop distance changes materially; exact revision threshold is unresolved.
- Stop is structurally behind the candle where Spike originated; exact wick/body/buffer is unresolved.
- Second leg is approximately/equally sized to first leg; source explicitly references AB=CD.
- Base target is TP1 / 1:1. TP2 is a larger management concept, not the frozen base target behavior.
- Source explicitly contrasts its candle-level AB=CD approach with classical internet/harmonic A/B/C/Fibonacci mapping; do not import classical anchors.

## What has been done

1. Source transcript was reconstructed and registered.
2. Source visual evidence was extracted and audited for P-Gap, entry, SL/origin, Leg-1/AB=CD, and real-trade examples.
3. Secondary public implementations were checked only as corroboration/contradiction evidence.
4. Semantic contract was frozen without inventing executable geometry.
5. Source-resolution closure matrix was created.
6. Synthetic discrimination infrastructure was created for all currently unresolved executable fields.
7. Guard tests were added so synthetic fixtures cannot select hypotheses by themselves and cannot use profitability as evidence.
8. Last-Spike-candle breakout/reclaim was explicitly rejected as a canonical prerequisite because it is secondary-only and not required by the primary source.
9. Entry/SL/real-trade cross-reference audits were added.
10. Latest local verification passed:
   - 48 test files passed
   - 189 tests passed
   - synthetic discrimination gate: 3/3 passed
   - focused source/geometry tests: 17/17 passed
   - `npm run build` / `tsc --noEmit` passed

## Current unresolved executable geometry

Do NOT invent any of these:

- P-Gap OHLC boundary/formula.
- P-Gap candle timing/index.
- P-Gap touch/equality rule.
- P-Gap minimum size.
- Entry candle identity.
- Entry exact price formula.
- Entry wick/body convention.
- Entry buffer.
- Pending-level revision threshold/semantics in numerical form.
- Fill/touch/cross/close semantics.
- Exact Spike-origin candle identity for every source variant.
- SL wick/body boundary.
- SL buffer/strictness.
- Leg-1 exact anchors.
- Leg-2 projection anchor.
- AB=CD numerical tolerance.
- Exact multi-position / 2X target-management behavior.
- Deterministic context/important-level detector.
- Any session filter.

## Synthetic discrimination gate

File: `tests/fixtures/SP2LSyntheticDiscrimination.fixtures.ts`

Currently covered fields:

- `PGAP_BOUNDARY`
- `PGAP_CANDLE_IDENTITY`
- `PGAP_TOUCH_RULE`
- `ENTRY_CANDLE_IDENTITY`
- `ENTRY_PRICE_CONVENTION`
- `ENTRY_REVISION_SEMANTICS`
- `FILL_TOUCH_SEMANTICS`
- `SL_BOUNDARY`
- `SPIKE_ORIGIN_IDENTITY`
- `LEG1_ANCHORS`
- `AB_CD_TOLERANCE`

Every fixture remains unresolved, requires source evidence to select, and is not production eligible.

## Current gate status

- SOURCE RESOLUTION: semantic contract complete; executable geometry incomplete.
- SYNTHETIC FIXTURES: PASS / READY / no hypothesis selected.
- FROZEN GEOMETRY: BLOCKED.
- DEV: LOCKED.
- UNTOUCHED VAL: LOCKED.
- ROBUSTNESS/STABILITY: LOCKED.
- FRESH HOLDOUT: LOCKED.
- PRODUCTION: UNCHANGED.

## Immediate next action

Continue a **primary-source discrimination pass**, starting with Entry Geometry because the source gives strong pending-limit semantics but exact price geometry remains unresolved.

Priority order:

1. Entry candle identity: previous/relevant vs first correction vs origin.
2. Entry price convention: wick extreme vs body edge.
3. Pending-level revision semantics: source-confirmed qualitative behavior vs any exact numerical rule.
4. Fill/touch semantics.
5. P-Gap boundary/timing/touch.
6. SL exact boundary and origin identity.
7. Leg-1 anchors and Leg-2 projection.
8. AB=CD tolerance.

For each item:

`primary-source observation -> synthetic fixture -> discriminate only if source genuinely distinguishes -> record timestamp/frame/evidence -> update source-resolution matrix -> tests -> only then consider Frozen Geometry.`

If the source does not discriminate, leave the field unresolved. Do not use backtest performance to choose among interpretations.

## Research path

`SOURCE RESOLUTION`
→ `SYNTHETIC FIXTURES`
→ `FROZEN GEOMETRY`
→ `DEV`
→ `UNTOUCHED VALIDATION`
→ `ROBUSTNESS / STABILITY`
→ `FRESH HOLDOUT`
→ `PRODUCTION`

Production and live signal generation must not begin before all required geometry is source-confirmed, deterministic, fixture-tested, DEV-validated, untouched-VAL-validated, robustness-tested, and fresh-holdout-confirmed.

## Canonical exclusions

Do not promote these without new primary-source evidence:

- generic FVG = P-Gap
- liquidity sweeps
- BOS/MSS
- displacement thresholds
- fixed spike-size thresholds
- 65% body rule
- mandatory last-Spike breakout/reclaim
- classical harmonic ABCD/Fibonacci mapping
- fixed 50% retracement as base entry
- session filters
- optimized thresholds selected from backtests

## Handoff instruction for next chat

Start by reading this snapshot and the source registry/transcript. Treat the source video at the recorded local path and its SHA256 as the already-established authoritative artifact. Do not ask the user to upload the video or transcript again unless the runtime genuinely no longer has the video and a new direct inspection is technically required. Resume from the immediate next action: primary-source discrimination of Entry Geometry.
