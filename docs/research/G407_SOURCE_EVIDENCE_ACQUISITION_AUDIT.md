# G407 — Source Evidence Acquisition Audit

## Purpose

G407 records the result of source-evidence recovery for the seven executable-geometry blockers carried by G400/G406.

This gate is deliberately **evidence-audit only**. It does not infer, optimize, or freeze executable geometry.

## Repository-wide recovery result

A branch-wide GitHub search for transcript/subtitle/source-video identifiers did not recover a complete provenance-identified transcript artifact.

The authoritative source registry was recovered on branch `research/source-aligned-sp2l-semantics-v1`:

- Source: `https://youtu.be/7HEC5mO3d3U`
- Registered source asset: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: `01:09:15.667`
- FPS: `30.0`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

The registry explicitly states that the MP4 has no embedded subtitle stream and that a complete transcript is not currently registered.

## Newly recovered external source-access evidence — 2026-09-14

A web search recovered two useful secondary-source indicators:

1. The YouTube page is explicitly titled `استراتژی SP2L Strategy (Subtitle)`, confirming that the published video is presented as a subtitle-bearing source at the page level. The YouTube page itself does not expose the subtitle transcript through the accessible text representation used in this audit.
2. A Telegram mirror/channel post states that an exact Persian subtitle for the video was prepared and added, and separately advertises a `SP2L_Spike_To_Leg_Two_Strategy.pdf` file (14.2 MB). These are **secondary/non-authoritative discovery leads only**; the subtitle text and PDF bytes were not recovered into a provenance-controlled project artifact during this pass.

The official creator page was also independently recovered and is already recorded in `SOURCE_OFFICIAL_WEB_CORROBORATION_2026-09-14.md`. It strengthens semantic evidence for P-Gap validity, the corrective-candle second-leg trigger, the spike-origin stop reference, and default 1:1 target, but does not resolve executable geometry.

**Important:** the existence claim for a subtitle/PDF artifact is not treated as evidence of its contents. No rule is promoted from the Telegram description, and no transcript quotation is used.

## Recovered visual evidence

The source frame register identifies the following high-value windows:

| Window | Evidence | Resolution status |
|---|---|---|
| 36:00–36:20 | `Valid BO = P-Gap`, examples 1/2/3 | P-Gap formula unresolved |
| 36:30–37:10 | explicit `AB=CD`, `1M / 5M` | equality confirmed; anchors/tolerance unresolved |
| 37:20–38:40 | directional movement → correction → continuation | A/B/C geometry unresolved |
| 38:40–40:20 | `Limit` / `Buy Limit`, horizontal level, `SL` | entry/stop mapping unresolved |
| 40:20–44:30 | order handling, TP1/TP2, SL | target mapping unresolved |

## Seven G400 blockers

1. `UNRES-PGAP-GEOMETRY` — **OPEN**
2. `UNRES-ABCD-ANCHORS` — **OPEN**
3. `UNRES-ABCD-TOLERANCE` — **OPEN**
4. `UNRES-ENTRY-PRICE` — **OPEN**
5. `UNRES-ENTRY-TIMING` — **OPEN**
6. `UNRES-STOP-BOUNDARY` — **OPEN**
7. `UNRES-TARGET-MAPPING` — **OPEN**

## Evidence interpretation

Source-confirmed semantics recovered by the audit:

- SP2L means Spike → 2 Leg.
- `AB=CD` is explicitly shown.
- `Valid BO = P-Gap` is explicitly shown.
- Pending-limit / `Buy Limit` entry is explicitly demonstrated.
- Structural SL is explicitly demonstrated.
- The official creator page states that the second-leg trigger is based on the corrective candle reaching the prior candle's low/high depending on direction.
- The official creator page states that the stop is behind the candle from which the spike originated.
- The official creator page states a default 1:1 risk-to-reward target.
- `2X` appears as a distinct module and is not promoted into the core target rule.

None of these observations uniquely specifies the unresolved executable OHLC geometry.

## Transcript status

**NOT RECOVERED / NOT REGISTERED.**

The search pass found evidence that subtitle material exists or was prepared, but not a provenance-controlled transcript artifact that can be quoted or used to resolve geometry.

## Gate decision

**G407 = BLOCKED — executable-geometry evidence acquisition remains incomplete.**

This result is intentionally fail-closed. G400 remains BLOCKED. No candidate P-Gap formula, A/B/C anchor, AB=CD tolerance, pending-limit price/fill rule, stop price, or target formula is promoted.

## Next action

The next source-resolution pass must acquire the actual subtitle/transcript or raw-video frames, preferably both, into a provenance-controlled artifact. Once acquired, inspect the registered windows 36:00–39:50 at sub-second granularity and reconcile each annotation change against the published creator wording. Preserve every observation as source evidence before converting any visual similarity into a deterministic rule.
