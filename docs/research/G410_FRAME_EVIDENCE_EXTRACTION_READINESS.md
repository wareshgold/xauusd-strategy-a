# G410 — Provenance-Controlled Frame Evidence Extraction Readiness

Date: 2026-09-14
Parent gate: G409
Status: BLOCKED_PENDING_FRAME_ARTIFACT

## Purpose

G410 defines the controlled extraction required to turn the already-registered source-video observations into reproducible frame artifacts. It does not infer or freeze trading geometry.

## Source asset

Video SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
FPS: `30.0`
Resolution: `640x360`
Duration: `01:09:15.667`

Nominal frame mapping: `round(timestamp_seconds * 30)`.
This mapping is an indexing convention only; transcript timestamps must not be treated as exact visual synchronization without inspection.

## Required extraction windows

| Window | Primary question |
|---|---|
| 34:14–35:50 | Which candle boundaries constitute the source P-Gap / pressure gap? |
| 36:15–37:10 | Which visual points are A/B/C and how is AB=CD drawn? |
| 38:18–39:48 | What exact source level receives Buy Limit and when is it cancelled before fill? |
| 41:18–42:40 | What visual price boundary is used for SL and how are TP1/TP2 positioned? |
| 1:04:19–1:04:32 | How does the later worked example map the deep-leg origin, entry, Leg 1 and R1/R2? |

## Existing immutable visual identifiers

Previously registered representative frames include:

- F3761 @ 01:02:41 — `ac4fa47c980ad64b97631accfcb84022773c9e4844ca28482e79186e45be41a5`
- F3773 @ 01:02:53 — `00125a655f1cd246fdfb0ec9e81b8b433dc8d617a28e2cd5ebfb9d58621dfd9a`
- F3779 @ 01:02:59 — `0b3b0ce1d967e81bb1334fe38cfd7173f56e29ec18849679fce8cebd3bed17d0`
- F3859 @ 01:04:19 — `a7aa9b16bffb3209a6ebab728fae0ab93f229fc7d6ec8f37638ab064b70593a6`
- F3868 @ 01:04:28 — `91140cd04c7a84ce48f21e90ddb102d5626b2063def9cb99a8d9666faad3f4a0`
- F3869 @ 01:04:29 — `a987b09cb58cbb04582bd85fd4905448a85d335f004e2e9022891a1b8cfc48b5`
- F3870 @ 01:04:30 — `d57324d2d211e2a29412d8502f1059a01bd1745e2f880aee97a1ed979c593fe7`
- F3872 @ 01:04:32 — `f65aef8f98c5be98d6a4c9f59df96c05221c9fa07acbd8d0f49d1f5de50ed17d`

These identifiers are evidence references only. They do not by themselves establish exact OHLC semantics.

## Extraction record schema

Every extracted frame artifact must record:

- source asset SHA-256;
- timestamp requested;
- actual decoded frame index;
- FPS and extraction tool/version;
- output image SHA-256;
- source file byte size when available;
- extraction command or reproducible method;
- observation text;
- confidence;
- whether the observation resolves a G400 blocker.

## Fail-closed rules

Do not promote any candidate because it visually resembles a conventional trading pattern.

Do not freeze:

- generic three-candle P-Gap;
- arbitrary A/B/C/D anchors;
- fill = C;
- arbitrary AB=CD tolerance;
- wick/body stop choice;
- arbitrary TP2 extension.

If the source video binary/frame image is unavailable to the execution environment, G410 must remain blocked rather than fabricating coordinates or hashes.

## Current result

The repository already contains semantic and source-visual audit history, including the deep-leg/parent-leg evidence and frame hashes. The current branch does not expose the raw MP4 or the required coordinate-level image artifacts to the GitHub text interface, so a reproducible extraction cannot honestly be claimed from this environment.

Therefore:

`G410 = BLOCKED_PENDING_FRAME_ARTIFACT`

`G400 = BLOCKED`

`FROZEN_GEOMETRY = NOT AUTHORIZED`

`DEV = NOT AUTHORIZED`

`VALIDATION = PROTECTED`

`PRODUCTION = BLOCKED`

## Next action

Obtain the registered raw-video asset or a provenance-controlled frame bundle in an environment capable of decoding it, then populate the extraction record and run the corresponding synthetic discrimination tests. Historical optimization remains prohibited until source geometry is frozen.
