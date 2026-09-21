# SP2L Raw Video Frame Audit — 2026-09-20

## Purpose

Formal record of a fresh, read-only audit pass over the raw primary source
video `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`, conducted
2026-09-20 against blockers **F10 / F11 / F12 / F14** and the **P-Gap**
dependency.

This document converts the audit's evidence report into repository form. It
answers, per finding:
- what was directly observed in a video frame (with timestamp);
- what was already established via transcript records (and is cited, not
  re-verified);
- what is genuinely new in this pass;
- what geometry remains unresolved.

It is **documentation only**:
- no PARTIAL finding is promoted to canonical rule;
- no formula, threshold, buffer, precedence, sizing, or fill rule is created;
- no strategy code is changed;
- no execution logic is defined.

STATUS vocabulary (as used by the resolution audits):
**SOURCE-CONFIRMED · SOURCE-SUPPORTED · PARTIAL / UNRESOLVED · UNRESOLVED**.

---

## Source basis and method

Source file: `strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`
(`C:\Users\Mr.Mirzaei\Downloads\Telegram Desktop\`, ~90MB).

Stream probe (`ffprobe`):
- video: H.264, 640×360, duration 4155.67s (≈ 1:09:16 — matches the indexed
  training artifact referenced in
  `SP2L_BATCH16_PRIMARY_ARTIFACT_EXTRACTION_2026-09-16.md`);
- audio: AAC;
- **no subtitle stream exists** despite "subtitle" in the filename — all
  on-screen text is burned in (English labels + handwritten Persian
  annotations).

Method: 17 single frames extracted with `ffmpeg` at transcript-referenced
timestamps into an out-of-repo temp dir (`sp2l-audit`), visually inspected.
Audio/speech was **not** re-transcribed in this pass (no transcription
capability); speech wording is cited from existing transcript records only.
At 640×360, handwritten Persian annotations are **not reliably
transcribable** and are never cited as wording evidence.

Related records (unchanged by this document):
- `SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `SP2L_SOURCE_FORENSICS_LEDGER_F09_F14_2026-09-16.md`
- `SP2L_BATCH17_UPLOADED_PRIMARY_VIDEO_EVIDENCE_F13_F14_2026-09-16.md`
- `SP2L_BATCH18_PRIMARY_ARTIFACT_FORENSIC_F8_F12_F15_2026-09-16.md`
- `SP2L_BATCH34_PRIMARY_SEQUENCE_GEOMETRY_FORENSIC_2026-09-17.md`
- `SP2L_BATCH36_PGAP_FORENSIC_SOURCE_RESOLUTION_2026-09-17.md`
- `SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md`
- `SP2L_SOURCE_DISCRIMINATION_REVIEW_MATRIX_2026-09-20.md`

---

## 1. Primary visual evidence (direct frame observations, this pass)

Each entry: timestamp — frame id — observation. Authority: PRIMARY SOURCE.
Confidence applies **only** to what is stated; anything beyond the visible
label is marked LOW / not evidence.

### F14 — AB=CD

- **36:45 (f3645):** title block "SP2L Strategy / Spike - 2Leg / Designed by
  MohammadAli Poursamadi"; handwritten circled "AB=CD"; 5-candle bullish
  schematic with **no A/B/C/D letters on any candle and no measurements**.
  HIGH confidence that AB=CD belongs to SP2L vocabulary; no anchor evidence.
- **37:00 (f3700):** same board plus "1M / 5M" annotation (timeframe context).
  No anchors, no measurement.
- **37:57 (f3757):** mid-drawing transition frame (whiteboard scribble,
  illegible). Not usable as evidence. Recorded to prevent future citation.

### P-Gap

- **36:45–37:00 (f3645, f3700):** printed label "Valid BO = P-Gap" pointing at
  the large breakout candle. HIGH confidence the equation exists on screen;
  LOW — no OHLC formula, indexing, or wick/body semantics visible.
- **34:25 (f3425):** "P-GAP" handwritten top-right; four 4–5 candle
  schematics; leftmost crossed with red X; three accepted without overlays.
- **35:37 (f3537):** same board annotated — two accepted groups circled with
  short horizontal strokes marking inter-candle zones. MEDIUM confidence that
  P-Gap is taught via accepted/rejected ordering variants; LOW — at 360p the
  stroke endpoints (body vs wick) cannot be resolved, so **no formula is
  cited**.
- **31:43 (f3143):** four bullish sequences; leftmost annotated with channel
  lines + arrow (rejected channel-like construction); no P-Gap label in this
  frame. Illustrative only (clean vs channel teaching).

### F10 — SL anchor / invalidation

- **39:48 (f3948):** handwritten "Buy Limit" with arrow to the horizontal
  reference line; handwritten "SL" with arrow pointing below the small
  origin candle's low; 3-candle structure circled. MEDIUM confidence: entry
  reference and SL anchor are distinct levels; SL sits behind/below the
  spike-origin extreme. LOW — no wick/body/buffer label; exact price field
  undetermined.
- **41:40 (f4140):** "Buy" arrow to black horizontal line; "2x" blue line
  lower; "SL" blue underline beneath origin-candle low. MEDIUM confidence in
  Buy > 2x > SL vertical ordering; no prices, no rules.
- **39:26 (f3926):** horizontal line through the large candle's body area,
  unlabeled. LOW — illustrative only.
- **38:38 (f3838):** horizontal base line below the sequence, curve arrow,
  tick marks at candle bases; no labels. LOW — illustrative only.
- **41:18 (f4118):** clean 5-candle sequence with horizontal reference line,
  no labels. Neutral.

### F11 — Pending-order lifecycle

- **40:57 (f4057):** circled numbers 1, 2, 3 beside a 4-candle sequence with
  horizontal reference line; the word "Delete" handwritten; Persian
  annotations present but not transcribable at this resolution. MEDIUM
  confidence: trigger/order handling is multi-variant and deletion is an
  author-acknowledged action. LOW — no mandatory/optional marking, no
  timeout, no replacement formula visible.

### F12 — Trigger family

- **36:15 (f3615):** four spike-candle schematics; leftmost red-X rejected;
  three accepted, circled and numbered 1, 2, 3; "Valid BO = P-Gap" label;
  gray shaded zones on accepted variants. MEDIUM confidence: acceptance is
  variant-based, not single-formula. Acceptance *criteria* per variant are
  not labeled — not inferred.
- **40:57 (f4057):** same 1/2/3 numbering beside the trigger sequence (see
  F11 above). Corroborates the trigger family; no precedence/selection rule
  visible.

### Worked live-chart segments (incl. bearish)

- **50:09 (f5009):** live dark-background chart; green target box ("0.0" top,
  "2x" bottom); blue circle around micro-candles at box base. No gap/SL
  labels in-frame. LOW — demonstration, not definition.
- **57:14 (f5714):** live chart with MA line; spike-origin low and swing
  annotations; no text labels. LOW — illustrative only.
- **1:04:00 / 1:04:32 (f6400, f6432):** bearish live chart with MA; f6432
  shows a short-position box with entry/SL lines (axis ≈ 3416 area). Bearish
  demonstrations exist, but carry **no labeled SL-anchor, trigger, AB=CD, or
  gap rule**. LOW — existence only.

---

## 2. Existing transcript-derived evidence (cited, not re-verified)

Speech wording below comes from the repo's established transcript records.
This pass did not re-transcribe audio; these items are preserved for
traceability and were **not** treated as new findings:

- 36:15 — strategy named SPIKE-2LEG, 2Leg concept equated with AB=CD; second
  leg expected to equal the first; target at second-leg completion.
- 31:43 — breakout candle associated with P-Gap; P-Gap distinguished from
  E-Gap; location matters.
- 34:25–35:37 — P-Gap/breakout relationship with multiple ordering variants.
- 38:38 — correction begins below the "first low"; order placeable there
  ("first" semantically ambiguous per
  `SP2L_VISUAL_GEOMETRY_TRIANGULATION_V3_2026-09-09.md`).
- 39:26 — return to the referenced area cancels the scenario.
- 39:48 — when a subsequent candle forms, the existing order *may* be deleted
  and a new order placed per changed stop distance (optionality unresolved).
- 40:57–41:03 — trigger family: one-, two-, three-candle structures plus
  bar/key-bar confirmation variants.
- 41:18 — activated position described with an SL.
- 38:05; 41:26–41:53; 57:14 — 2X as optional later entry; approximate
  half-target-distance concept (no executable anchor/formula).
- 50:09 — early/trend-positioned P-Gap distinguished from E-Gap (no formula).
- 1:04:00–1:04:32 — worked trade with Lower-High sequence, order, activation,
  Leg-1 reference (visual coordinates not machine-readable from text).

---

## 3. Newly discovered evidence (genuinely new in this pass)

Strictly new items — each is a **citation upgrade, not a rule**:

- **N-01:** author-hand-labeled "Buy Limit" and "SL" co-occurring in a single
  frame (39:48, f3948). Hardens the *separation* claim to direct single-frame
  evidence. F10 stays PARTIAL — no price field.
- **N-02:** author-hand-labeled Buy > 2x > SL vertical ordering in a single
  frame (41:40, f4140). F10/F13 context only — no prices, no rules.
- **N-03:** author-numbered trigger variants 1/2/3 with handwritten "Delete"
  in a single frame (40:57, f4057). F11/F12 context only — no precedence, no
  lifecycle predicate.
- **N-04 (negative finding):** the file contains **no subtitle stream**
  (video + audio only). Future "subtitle extraction" expectations should
  target burned-in text/frames, not a text track.
- **N-05 (negative finding):** frame 37:57 is a mid-drawing transition and
  must not be cited as geometry evidence.

**No executable geometry rule was discovered.** Nothing in N-01–N-05 selects
a price field, event semantic, formula, or tolerance.

---

## 4. Still unresolved geometry (blockers unchanged)

| Blocker | Status | Exact missing evidence |
|---|---|---|
| F10 SL anchor | PARTIAL / UNRESOLVED | wick vs body vs open/close; buffer; touch vs penetration vs close invalidation; fixed vs dynamic; labeled bearish SL frame |
| F11 pending lifecycle | PARTIAL / UNRESOLVED | creation event; mandatory vs optional deletion; timeout/candle-count; replacement-price formula; candidate precedence |
| F12 trigger precedence | PARTIAL / UNRESOLVED | selection rule among variants 1/2/3; activation event (touch/close/breakout); complete bullish + bearish definitions |
| F14 AB=CD | PARTIAL / UNRESOLVED | A/B/C/D point identities; endpoint price semantics; observed-D vs projected-D; swing/pivot definition; equality tolerance |
| P-Gap | UNRESOLVED | OHLC/index formula; body-vs-wick endpoints; bullish measurement; bearish counterpart frame; P-Gap vs E-Gap boundary rule |

No blocker moves to READY on the basis of this pass. Highest-value next
acquisition remains: a labeled bearish worked example, and any
frame/statement giving an OHLC-anchored definition (SL field, gap endpoints,
A/B/C/D points).

---

## Frozen Geometry decision

**STILL_BLOCKED** — this pass corroborates every existing PARTIAL concept
finding and adds three single-frame citations (N-01–N-03), but yields zero
executable geometry rules. There is nothing to promote to frozen geometry,
and nothing in the sampled frames contradicts the current
PARTIAL/UNRESOLVED matrix.

---

## Frame inventory (provenance)

17 frames, 640×360 PNG, out-of-repo temp dir (`sp2l-audit`, retained for
reuse; not committed):

| Frame id | Timestamp | Subject |
|---|---|---|
| f3143_pgap | 31:43 | clean vs channel sequences |
| f3425_pgap | 34:25 | P-GAP board, clean |
| f3537_pgap | 35:37 | P-GAP board, annotated |
| f3615_naming | 36:15 | 4 spike variants, 1 rejected + 3 numbered |
| f3645_abcd | 36:45 | AB=CD label + Valid BO = P-Gap |
| f3700_equalleg | 37:00 | same + 1M/5M annotation |
| f3757_abcd | 37:57 | transition frame, unusable |
| f3838_correction | 38:38 | correction sequence, base line |
| f3926_invalidation | 39:26 | reference line through body |
| f3948_orderreplace | 39:48 | "Buy Limit" vs "SL" labels |
| f4057_trigger | 40:57 | 1/2/3 variants + "Delete" |
| f4118_sl | 41:18 | sequence + reference line, unlabeled |
| f4140_2x | 41:40 | Buy > 2x > SL ordering |
| f5009_pgap_egap | 50:09 | live target-box demo |
| f5714_2x | 57:14 | live MA-chart demo |
| f6400_worked | 1:04:00 | bearish live chart |
| f6432_worked | 1:04:32 | bearish short-position box |
