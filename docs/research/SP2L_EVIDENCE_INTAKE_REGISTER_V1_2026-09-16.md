# SP2L Evidence Intake Register V1 — 2026-09-16

## Purpose

Central register for all future primary-source evidence submissions against the seven Frozen Geometry blockers.

## Current register

| Evidence ID | Field | Source | Timestamp/frame | Discrimination result | Promotion | Status |
|---|---|---|---|---|---|---|
| `E-20260916-BASE-001` | `entry` | Existing primary transcript | 38:38–39:26 | Correction/Limit behavior supported, exact universal entry anchor not uniquely determined | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| `E-20260916-BASE-002` | `invalidation` | Existing primary transcript | 38:53–39:26 | Return to referenced level invalidates scenario; exact OHLC anchor/buffer unresolved | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| `E-20260916-BASE-003` | `limitRefresh` | Existing primary transcript | 39:48 | Refresh behavior described; mandatory threshold unresolved | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| `E-20260916-BASE-004` | `trigger` | Existing primary transcript | 40:57–41:03 plus trigger-family evidence | Trigger family and variants supported; deterministic classifier/precedence unresolved | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| `E-20260916-BASE-005` | `twoX` | Existing primary transcript | 38:05; 41:26–41:53; 57:14 | Optional later entry and approximate half-target concept supported; exact anchor/sizing/fill unresolved | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| `E-20260916-BASE-006` | `abcd` | Existing primary transcript | 36:15; 36:59–37:08; 37:57 | Two-leg/AB=CD concept and equal-leg expectation supported; anchors/tolerance unresolved | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |
| `E-20260916-BASE-007` | `pGap` | Existing primary transcript | 31:43; 34:25–35:37; 50:09 | P-Gap/E-Gap distinction and breakout relationship supported; exact OHLC formula unresolved | No | `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED` |

## Register rules

1. Every new evidence item receives a unique ID.
2. Source observations are recorded before interpretation.
3. Competing interpretations must be preserved until primary evidence discriminates them.
4. A field can be `SOURCE_CONFIRMED` only when executable meaning is uniquely determined.
5. No evidence item may promote geometry based on backtest performance.
6. This register never authorizes execution or BUY/SELL generation.

## Current gate summary

- Required fields: 7
- `SOURCE_CONFIRMED`: 0
- `PARTIAL_MORE_PRIMARY_EVIDENCE_REQUIRED`: 7
- Frozen Geometry: `BLOCKED`

## 125R integrity

The 125R observation is not modified, clipped, excluded, or reclassified by this register.
