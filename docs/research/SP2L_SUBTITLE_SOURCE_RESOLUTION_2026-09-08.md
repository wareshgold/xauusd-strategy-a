# SP2L Subtitle Source Resolution

Date: 2026-09-08
Branch: `research/source-resolution-entry-level-v2`

## Purpose

Determine whether the Persian subtitle/transcript referenced by the public distribution of the SP2L source video can be recovered or directly inspected, and whether it can be used to resolve the remaining Spike / P-Gap / A-B-C-D geometry questions.

## Source identity

The public Telegram distribution identifies the same 1:09:16 SP2L video and links the YouTube source `7HEC5mO3d3U`. The indexed channel post lists the video syllabus, including:

- four Spike candle types;
- P-Gap;
- combining 2L with Spike;
- order placement;
- 2X;
- Level/context combinations;
- ten entry examples on 13 May 2025;
- detailed review of the four trades performed at the beginning of the video.

The same public channel later explicitly states that a **"دقیق فارسی مخصوص ناشنوایان"** Persian subtitle was prepared and added.

## Retrieval result

The indexed Telegram page exposes the subtitle announcement and surrounding post text, but it does not expose the subtitle file contents, an `.srt`/`.vtt` attachment, or timestamped transcript text through the accessible web representation.

The YouTube page is also identifiable as the same SP2L video, but the accessible page representation does not expose caption-track contents or a transcript.

The uploaded local MP4 was independently checked previously with `ffprobe`: it contains no embedded subtitle stream. Therefore the local asset cannot currently supply the Persian subtitle as an embedded track.

## Evidence status

| Artifact | Status | Use |
|---|---|---|
| Original uploaded MP4 | AVAILABLE | Primary visual/audio source |
| Embedded subtitle stream | ABSENT | Cannot extract from MP4 |
| Public Telegram subtitle announcement | CONFIRMED | Proves subtitle version exists publicly |
| Subtitle text/file through indexed Telegram page | NOT EXPOSED | Cannot treat as recovered transcript |
| YouTube transcript/caption text through accessible page | NOT EXPOSED | No direct transcript evidence |

## Important source boundary

The existence of the Persian subtitle is now a **confirmed research lead**, not a recovered source artifact. We must not reconstruct missing subtitle wording from third-party summaries and then label it as source-confirmed.

In particular, the following remain unresolved despite third-party claims:

- exact names/rules of the four Spike variants;
- executable P-Gap candle/price boundaries;
- exact A/B anchors;
- exact C anchor and whether C equals the Buy Limit level;
- exact D construction;
- numeric AB=CD tolerance.

## What the public distribution confirms

The public syllabus confirms that the source explicitly teaches four Spike types, P-Gap, SP2L order placement, 2X, Level/context combinations, ten entries on 13 May 2025, and a detailed review of the four initial trades. This makes those video regions high-value targets for manual source resolution.

## Next highest-value action

Obtain the actual subtitle artifact (SRT/VTT/text) from the subtitle-bearing distribution or from the subtitle-bearing video itself, then align its timestamps to approximately:

- 29:00–35:30 — four Spike examples / P-Gap teaching;
- 36:00–41:50 — AB=CD / Limit / Buy Limit / SL;
- 42:00–54:00 — real-chart examples and execution;
- 54:00–65:00 — additional examples / order history / 13 May 2025 examples.

Only after direct timestamped wording is available should unresolved geometry be promoted from hypothesis to canonical candidate.

## Gate impact

Source Resolution remains OPEN but materially narrowed. The missing subtitle artifact is now a tracked external-source recovery item. No production or canonical strategy code is changed by this document.

### Sources

- Public SP2L Telegram distribution: https://t.me/s/pur_samadi?after=1512
- YouTube source video: https://youtu.be/7HEC5mO3d3U
- Official SP2L page: https://poursamadi.com/sp2l-strategy/
