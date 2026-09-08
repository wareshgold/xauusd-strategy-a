# SP2L Source — Treasure Path

Date registered: 2026-09-08

## Purpose

This is the persistent source-asset registry for Strategy A / SP2L. It exists so future research sessions do **not** ask the user to re-upload the same full source video merely to recover source context.

The source asset itself is user-supplied conversation media; GitHub stores the deterministic fingerprint and source map, not a copy of the binary video.

## Canonical source identity

- Strategy: SP2L
- Meaning used by the current source ledger: Spike → 2 Leg
- Primary YouTube source: https://youtu.be/7HEC5mO3d3U
- Official creator site: https://poursamadi.com/sp2l-strategy/
- Full source video supplied in chat: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Source video duration: 01:09:15.667
- Video frame rate: 30.000 fps
- Total video frames: 124,670
- Resolution: 640×360
- Video codec: H.264
- Audio: AAC, 44.1 kHz, stereo
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- File size at registration: 89,959,245 bytes

## Important persistence rule

When a future chat needs source inspection, refer to this document and the source identity above first. Do not ask the user to re-upload the source unless the actual conversation attachment is unavailable to the runtime or a new higher-resolution source is specifically required.

## Exact frame addressing

The source is deterministic at 30 fps. For a timestamp `t` seconds, the nominal zero-based frame is:

`frame ≈ round(t × 30)`

For exact source work, always record both:

- human timestamp `HH:MM:SS.mmm`
- zero-based frame number

Do not rely on approximate descriptions such as “around minute 37”.

## Evidence logging convention

Future visual evidence should be registered as:

| Field | Required meaning |
|---|---|
| Source ID | `SP2L_FULL_2026-09-08` |
| Timestamp | exact `HH:MM:SS.mmm` |
| Frame | exact/nominal frame index |
| Visual claim | what is visibly shown |
| Source meaning | semantic interpretation supported by the source |
| Geometry status | confirmed / unresolved / candidate |
| Confidence | direct / strong / weak |
| Rule impact | canonical / research-only / blocker |

## Current source map

The full video is now available for frame-by-frame source resolution. Priority regions remain:

1. Opening definition and strategy introduction.
2. Four candle-spike types.
3. P-Gap explanation.
4. 2L + Spike construction.
5. Order placement / pending-limit mechanics.
6. 2X explanation.
7. Levels and context.
8. Trigger discussion.
9. Ten-entry example from 13 May 2025.
10. Detailed reconstruction of the first four trades.
11. Closing remarks.

These topic labels are a navigation aid from the published source description; they are **not** by themselves canonical geometric rules.

## Current geometry status

### Confirmed

- SP2L / Spike → 2 Leg naming and concept.
- `AB = CD` relationship is explicitly shown in the source material already inspected.
- Valid breakout is associated with P-Gap.
- Correction precedes the second leg.
- Pending-limit order placement is demonstrated in the source material already inspected.

### Still unresolved

- Exact G4 A/B OHLC anchors.
- Exact G5 C anchor.
- Executable P-Gap boundaries/formula.
- Any numerical AB=CD tolerance.
- Whether any execution price is identical to a geometric source anchor.

### Explicit prohibitions

- Do not substitute a generic three-candle imbalance for P-Gap.
- Do not choose A/B/C because a backtest performs better.
- Do not assume fill price = C.
- Do not invent an AB=CD tolerance.
- Do not replace pending-limit semantics with a close-reclaim trigger.

## Transcript status

The supplied MP4 contains video + audio streams but no embedded subtitle stream. The filename includes `subtitle`, but that is not evidence that subtitles are embedded in the MP4 container. Therefore a full transcript is **not claimed** here.

If a complete Persian subtitle/transcript file is later supplied, it should be stored beside this registry and linked here as a separate source artifact. The transcript must remain provenance-separated from the raw video and must not silently override visual source evidence.

## Source hierarchy

1. Raw authoritative source video.
2. Exact extracted frames from the source video.
3. Source transcript/subtitles, when available and provenance-identified.
4. Source ledger / canonical meaning map.
5. Frozen deterministic specification.
6. Implementation.
7. Historical research.

Backtest results never determine what the source means.

## Gate state at registration

- Source asset recovery: **COMPLETE**
- Frame-addressable source: **COMPLETE**
- Transcript: **NOT YET REGISTERED**
- G4 A/B: **UNRESOLVED**
- G5 C: **UNRESOLVED**
- P-Gap executable geometry: **UNRESOLVED**
- AB=CD semantic relationship: **CONFIRMED**
- Synthetic discrimination fixtures: **COMPLETE**
- Canonical geometry freeze: **BLOCKED**
- DEV: **BLOCKED for canonical SP2L**
- Untouched VAL: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **UNCHANGED**

## Source recovery note

The user explicitly requested that this full source be registered persistently because uploading it over the available internet connection took approximately 30 minutes. This request is part of the research provenance record: future sessions should use this registry rather than casually requesting the same asset again.
