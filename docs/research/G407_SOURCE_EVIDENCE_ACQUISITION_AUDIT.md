# G407 — Source Evidence Acquisition Audit

## Purpose

G407 records the result of a branch-wide source-evidence recovery pass for the seven executable-geometry blockers carried by G400/G406.

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
- `2X` appears as a distinct module and is not promoted into the core target rule.

None of these observations uniquely specifies the unresolved executable OHLC geometry.

## Transcript status

**NOT RECOVERED / NOT REGISTERED.**

No transcript-derived statement is used to resolve any blocker.

## Gate decision

**G407 = BLOCKED — evidence acquisition incomplete for executable geometry.**

This result is intentionally fail-closed. G400 remains BLOCKED. No candidate P-Gap formula, A/B/C anchor, AB=CD tolerance, pending-limit price/fill rule, stop price, or target formula is promoted.

## Next action

The next source-resolution pass should use the registered raw video and exact frame addressing to inspect annotation changes in 36:00–39:50 at sub-second granularity, while preserving every observation as source evidence rather than converting visual similarity into a deterministic rule.
