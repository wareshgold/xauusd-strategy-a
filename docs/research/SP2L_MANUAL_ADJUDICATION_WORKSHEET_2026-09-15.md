# SP2L Manual Adjudication Worksheet — 2026-09-15

## Purpose

Human-review worksheet for the source-grounded evidence candidate package. This document records review questions and a conservative provisional assessment; it does not itself promote geometry.

## Rule

A candidate is `SOURCE_DISCRIMINATED` only when the cited source uniquely and reproducibly determines the relevant executable dimension without invention. Otherwise it remains `REMAINS_BLOCKED`.

## Provisional review matrix

| Candidate | Dimension(s) | Source evidence | Conservative assessment | Reason |
|---|---|---|---|---|
| C01-PGAP-003 | p_gap | 00:36:30 / frame 65700: `Valid BO = P-Gap` | REMAINS_BLOCKED | Semantic role is explicit; executable OHLC boundary is not uniquely specified. |
| C02-ENTRY-SL-003 | entry_anchor, structural_invalidation | 00:39:40–00:40:20 / frames 71400–72600: Buy Limit, lower SL reference, horizontal level, Delete | REMAINS_BLOCKED | Entry and lower invalidation/SL roles are distinguishable, but exact price/candle boundary and fill semantics are unresolved. |
| C03-ABCD-MAG-003 | abcd_anchors, abcd_tolerance, leg2_start | 00:36:30–00:37:00 / frames 65700–66600: `AB=CD`; transcript supports Leg-2 equals Leg-1 magnitude | REMAINS_BLOCKED | Magnitude semantics narrow the hypothesis, but anchors, tolerance, and exact Leg-2 start are not uniquely reproducible. |
| C04-TARGETS-003 | targets_2x | 00:42:30 / frame 76500 plus 00:58:04–00:59:08 | REMAINS_BLOCKED | TP1/TP2/2X concepts are explicit, but executable formulas/anchors are unresolved. |
| C05-BEARISH-MIRROR-003 | bearish_mirror | 01:02:41–01:04:32 | REMAINS_BLOCKED | Bearish examples exist; complete deterministic mirror mapping would require inference. |
| C06-PENDING-REFRESH-003 | pending_refresh | 00:40:20 / frame 72600 plus related transcript windows | REMAINS_BLOCKED | Delete/lifecycle behavior is demonstrated, but delete/replace/retain conditions are not uniquely specified. |
| C07-TRIGGER-FAMILY-003 | trigger_classifier | 00:35:10–00:36:31 | REMAINS_BLOCKED | Multiple 1/2/3-candle constructions are shown, but exhaustive deterministic classifier conditions are unresolved. |
| C08-CORRECTION-INVALIDATION-003 | structural_invalidation, entry_anchor | 00:38:38–00:39:48 | REMAINS_BLOCKED | Relationship among correction, pending entry and invalidation is supported, but exact OHLC boundaries are unresolved. |

## Human adjudication requirement

The table above is a conservative review worksheet, not an autonomous canonical decision. The human adjudicator must independently confirm each candidate against the source artifact and may change the outcome only when the source provides a reproducible discriminator.

If the source does not provide that discriminator, the correct result is `REMAINS_BLOCKED`, preserving the unresolved hypotheses.

## Freeze implication

With the conservative assessments above, none of the ten Strategy A geometry dimensions is authorized for freeze. This worksheet does not authorize implementation, backtesting-based selection, execution, or BUY/SELL generation.
