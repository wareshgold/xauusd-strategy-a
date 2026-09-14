# G407 — Source Evidence Acquisition Audit

## Purpose

G407 records the result of source-evidence recovery for the seven executable-geometry blockers carried by G400/G406.

This gate is deliberately **evidence-audit only**. It does not infer, optimize, or freeze executable geometry.

## Recovery result

The previously missing provenance-identified transcript has now been recovered in the project File Library:

- File: `پورصمدیSP2L TRANSCIBE.txt`
- Created: 2026-09-12
- Timestamped Persian transcript of the SP2L source video
- Source video identity: `https://youtu.be/7HEC5mO3d3U`

The transcript is now available as a source-evidence artifact and is separately analyzed in `G408_SOURCE_TRANSCRIPT_RESOLUTION.md`.

The raw source registry remains:

- Registered source asset: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
- Duration: `01:09:15.667`
- FPS: `30.0`
- SHA-256: `ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`
- The registered MP4 has no embedded subtitle stream.

## Recovery correction

The previous G407 conclusion that the transcript was `NOT RECOVERED / NOT REGISTERED` is superseded by the recovery recorded on 2026-09-14.

The transcript is not being treated as self-authenticating raw source material. Its timestamps and content are used as source evidence and must still be reconciled against the raw video / exact-frame register whenever visual geometry is ambiguous.

## Critical transcript evidence now recovered

The 31:00–45:00 window contains direct source statements covering:

- breakout and follow-through;
- P-Gap as a pressure gap distinct from E-Gap;
- two P-Gap timing constructions treated as one strategy;
- Spike → correction → second leg;
- explicit `AB=CD` / Leg1 = Leg2;
- correction reaching below the first low in the bullish example;
- pre-placed Buy Limit during the first three candles;
- pre-fill invalidation if price returns to the referenced invalidating area;
- Buy + SL activation;
- TP1 / TP2 distinction;
- default preference for TP1 and a statement that TP should be 1 when the stop is relatively large.

These findings materially narrow several G400 blockers but do not uniquely specify all executable OHLC geometry.

## Recovered visual evidence

| Window | Evidence | Resolution status |
|---|---|---|
| 31:02–35:50 | breakout / follow-through / P-Gap timing and sequence | semantics strongly resolved; executable P-Gap formula unresolved |
| 36:15–37:10 | explicit AB=CD / Leg1 = Leg2 | relationship confirmed; anchors/tolerance unresolved |
| 37:20–38:40 | correction → second leg; first-low reference | event semantics strengthened; exact anchor/price unresolved |
| 38:40–40:20 | Buy Limit, order timing, invalidation, SL | entry timing strongly informed; exact price/fill/stop boundary unresolved |
| 41:18–42:48 | Buy activation, SL, TP1/TP2, default TP preference | target semantics strengthened; exact TP geometry unresolved |
| 1:04:19–1:04:32 | later explicit reward-1 target example | 1R target convention strongly corroborated |

## Seven G400 blockers

1. `UNRES-PGAP-GEOMETRY` — **OPEN / NARROWED**
2. `UNRES-ABCD-ANCHORS` — **OPEN / NARROWED**
3. `UNRES-ABCD-TOLERANCE` — **OPEN**
4. `UNRES-ENTRY-PRICE` — **OPEN / NARROWED**
5. `UNRES-ENTRY-TIMING` — **PARTIALLY RESOLVED / FRAME RECONCILIATION REQUIRED**
6. `UNRES-STOP-BOUNDARY` — **PARTIALLY RESOLVED / EXACT PRICE OPEN**
7. `UNRES-TARGET-MAPPING` — **PARTIALLY RESOLVED / EXACT GEOMETRY OPEN**

## Gate decision

**G407 = PASS for transcript acquisition.**

G407 no longer blocks because the critical transcript has been recovered. This does **not** clear G400. G400 remains **BLOCKED** until source geometry is frozen through transcript ↔ exact-frame reconciliation.

No candidate P-Gap formula, A/B/C anchor, AB=CD tolerance, exact pending-limit price/fill rule, exact stop price, or TP1/TP2 projection formula is promoted.

## Next action

Proceed to **G409 — transcript ↔ exact-frame reconciliation**, concentrating on:

1. 34:14–35:50 for P-Gap construction;
2. 36:15–37:10 for AB=CD visual anchors;
3. 38:18–39:48 for first-low entry and pre-fill invalidation;
4. 41:18–42:48 for SL and TP1/TP2;
5. 1:04:19–1:04:32 for the explicit 1R target example.

The reconciliation must remain source-evidence only until competing geometric interpretations are explicitly discriminated.
