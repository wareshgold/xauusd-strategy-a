# SP2L Subtitle Source Resolution

Date: 2026-09-08  
Branch: `research/source-resolution-entry-level-v2`

> **SUPERSEDED (2026-09-08):** This document records the earlier state in which the Persian subtitle/transcript had not yet been recovered. The full timestamped Persian transcript is now recovered and registered at `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`. Use `docs/source/treasure_path/SP2L_SOURCE_TRANSCRIPT_REGISTRY_2026-09-08.md` and `docs/research/SP2L_SOURCE_RESOLUTION_SNAPSHOT_2026-09-08.md` as the current source-resolution entry points.

## Historical purpose

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

## Historical retrieval result

At the time this document was written, the indexed Telegram page exposed the subtitle announcement but not the subtitle file contents, and the accessible YouTube page did not expose caption-track contents. The uploaded local MP4 also contains no embedded subtitle stream.

That historical state is now superseded by the later discovery of the full timestamped Persian transcript in the repository.

## Current recovered source artifact

- Raw transcript: `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
- Transcript SHA: `47f867385338738a23b2d06dc48e67b852127243`
- Transcript registry: `docs/source/treasure_path/SP2L_SOURCE_TRANSCRIPT_REGISTRY_2026-09-08.md`
- Durable snapshot: `docs/research/SP2L_SOURCE_RESOLUTION_SNAPSHOT_2026-09-08.md`

The transcript is now the primary semantic research artifact. It is source material, not by itself a frozen executable geometry specification.

## What the recovered transcript materially resolves

The recovered wording directly confirms:

- around 30:53–31:18, a valid breakout is described as a close beyond a prior level followed by a follow-through/key bar that cannot return into the prior range;
- around 34:14–34:35, P-GAP is presented as a visual marker for where breakout occurred, and a gap is described when the referenced high and low do not overlap, associated with breakout + follow-through;
- around 35:50–36:15, multiple spike constructions are treated as a hierarchy/sequence of movements and are all treated as Spike for this strategy;
- around 36:15–36:59, SP2L is explicitly tied to 2Leg / AB=CD, with the source emphasizing candle-level work rather than a generic classical implementation;
- around 36:59, the expected second leg is stated to match the first leg;
- around 38:38–39:26, correction is described as moving below the first low for the bullish example, and the order may be placed manually or as a pre-set Limit during correction;
- around 39:26, Buy Limit is explicitly named and the stop/invalidation distance is known before activation; returning to the invalidation area invalidates the scenario;
- around 39:48–40:07, pending-order management can involve deleting/replacing the order if the risk distance changes materially.

These statements strengthen semantic resolution but still do not freeze the exact P-Gap formula, A/B/C/D OHLC anchors, AB=CD tolerance, or historical intrabar fill semantics.

## Evidence status after recovery

| Artifact | Status | Use |
|---|---|---|
| Original uploaded MP4 | AVAILABLE | Primary visual/audio source |
| Embedded subtitle stream | ABSENT | Not available inside MP4 |
| Public Telegram subtitle announcement | CONFIRMED | Proves subtitle version exists publicly |
| Full timestamped Persian transcript | **RECOVERED / REGISTERED** | Primary semantic source artifact |
| Transcript registry | **CONFIRMED** | Provenance/navigation |
| YouTube transcript via page | NOT NEEDED | Recovered repository transcript supersedes this retrieval path |

## Remaining source blockers

The following remain unresolved despite the recovered transcript:

- exact names/rules of the four Spike variants;
- executable P-Gap candle/price boundaries;
- exact A/B anchors;
- exact C anchor and whether C equals the Buy Limit level;
- exact D construction;
- numeric AB=CD tolerance;
- exact intrabar fill semantics;
- exact target relationship among base 1:1, TP1/TP2 and the separate 2X module;
- exact rejection predicate represented by visual invalid examples.

## Gate impact

The subtitle-retrieval blocker is **CLOSED** because the full timestamped transcript is now recovered and registered. The overall Source Resolution gate remains **OPEN** because executable geometry is still unresolved. No production or canonical strategy code is changed by this document.

### Sources

- Public SP2L Telegram distribution: https://t.me/s/pur_samadi?after=1512
- YouTube source video: https://youtu.be/7HEC5mO3d3U
- Official SP2L page: https://poursamadi.com/sp2l-strategy/
- Recovered transcript: `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`
