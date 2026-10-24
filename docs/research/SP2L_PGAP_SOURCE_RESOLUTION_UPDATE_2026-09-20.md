# SP2L P-Gap Source Resolution Update — 2026-09-20

## Purpose

Formalize the findings of the read-only dependency audit over the author gap
video (`gap پورصمدی دوره جامع.mp4`) into a repository artifact. This document
records what the gap video establishes about P-Gap, what changed relative to
the previous P-Gap status, what remains unresolved, and what follows for
Frozen Geometry and the existing P-Gap implementation.

It answers, for P-Gap only:
- what the source provenance is;
- what new evidence is confirmed;
- what P-Gap means according to the author;
- what changed from the previous status;
- what remains unresolved;
- the impact on Frozen Geometry;
- the impact on the existing implementation.

It is **documentation only**:
- no OHLC formula is created;
- no candle index is created;
- no detector is proposed;
- no trading rule is created;
- no code is changed;
- nothing unresolved is promoted to canonical.

STATUS vocabulary (as used by the resolution audits):
**SOURCE-CONFIRMED · SOURCE-SUPPORTED · PARTIAL / UNRESOLVED · UNRESOLVED**.

Governing principle: **source outranks implementation**. Concept status and
executable-geometry status are tracked separately: the P-Gap *concept* can
move to SOURCE-CONFIRMED while executable geometry stays BLOCKED.

---

## 1. Source provenance

Source file: `gap پورصمدی دوره جامع.mp4`
(`C:\Users\Mr.Mirzaei\Downloads\`, ~44MB).

Stream probe (`ffprobe`):
- video: H.264, 854×480, duration 1955.79s (≈ 32:36);
- audio: AAC;
- **no subtitle stream** — all on-screen text is burned in.

The video is a branded Poursamadi comprehensive-course lesson
("PriceAction (Gaps)", poursamadi.com) — author-associated primary material.
It is the target of the SP2L training video's own deferral at 31:55
("if you don't know E-GAP and P-GAP, watch the gaps video"), recovered from
transcript blob `47f867385338738a23b2d06dc48e67b852127243`.

Method: 29 single frames extracted with `ffmpeg` into an out-of-repo temp
dir (`sp2l-audit/gap`), visually inspected. No transcript of this video
exists in the repo and no local speech-to-text capability exists, so audio
content is **unaudited** (stated limitation). Evidence below is visual:
author-written burned-in slide text plus marked charts. Authority for slide
text: PRIMARY SOURCE.

Related records (unchanged by this document):
- `SP2L_PRIMARY_SOURCE_TRANSCRIPT_2X_TRIGGER_ABCD_2026-09-16.md`
- `SP2L_BATCH36_PGAP_FORENSIC_SOURCE_RESOLUTION_2026-09-17.md`
- `SP2L_PGAP_SOURCE_EVIDENCE_CLOSURE_ATTEMPT_2026-09-19.md`
- `SP2L_PGAP_FINAL_SOURCE_BOUNDARY_AUDIT_2026-09-19.md`
- `SP2L_F10_F11_F12_F14_EVIDENCE_GAP_MATRIX_2026-09-20.md`
- `SP2L_RAW_VIDEO_FRAME_AUDIT_2026-09-20.md`

---

## 2. New confirmed evidence

### G-01 — General gap-detection convention (slide header)

- Location: ~17:00 (survey frame `g_1020`).
- Exact visible text: «به فاصله بین سقف ۲ کندل قبل و کف کندل حاضر دقت کنید که اگر فاصله داشت گپ ایجاد شده است»
  ("Watch the distance between the HIGH of 2 candles ago and the LOW of the
  current candle — if there is distance, a gap has formed." Blue rectangles
  mark the zones; yellow candles highlight instances.)
- Authority: PRIMARY SOURCE. Confidence: HIGH (text) / LOW (endpoints).
- Confirms: the author's gap-detection convention uses a **2-candle
  lookback: high[−2] vs low[0]**.
- Does NOT confirm: wick vs body (unresolvable at 480p); the bullish mirror
  (low[−2] vs high[0] — never shown); which gap *type* this convention
  governs (header says «گپ» generically).

### G-02 — Four-type gap taxonomy (author's own classification)

- Locations: ~19:40 (taxonomy slide «انواع گپ», frame `q_1180`, items circled
  progressively) and ~31:00 (summary slide, frame `g_1860`).
- Exact visible text: **بریک اوت، فشار، خستگی، معمولی**
  (breakout, pressure, exhaustion, common).
- Authority: PRIMARY SOURCE. Confidence: HIGH.
- Confirms the mapping: **P-GAP = «فشار» (pressure)**,
  **E-GAP = «خستگی» (exhaustion)**. The SP2L video's "P-Gap vs E-Gap"
  distinction maps onto this taxonomy.

### G-03 — Breakout-gap definition (text slide + worked example)

- Location: ~20:00 (definition slide, frame `q_1200`); worked ~20:20–22:00
  (frames `q_1220`, `q_1320`).
- Exact visible text: «زمانیکه یک گپ در ابتدای یک حرکت ایجاد می شود، آن یک
  **بریک اوت گپ** است» + «"بریک اوت گپ" صعودی» + «در این حالت قیمت بسته شدن
  این کندل در سقف قبلی است»
  ("When a gap forms at the START of a move, it is a breakout gap" — bullish
  case: "the closing price of this candle is at the previous high.")
- Authority: PRIMARY SOURCE. Confidence: HIGH (definition) / MEDIUM
  (close-at-previous-high stated for the bullish case only).
- Confirms: gap-at-move-start = breakout gap; a close-location condition
  (bullish).
- Does NOT confirm: P-Gap endpoints; the bearish close condition in text.

### G-04 — Pressure-gap definition (text slide; the P-Gap answer)

- Location: ~22:20 (frames `q_1340`, `q_1360`).
- Exact visible text: «**گپ فشار** — وقتی بعد از **۱۰ الی ۳۰ کندل** در روند
  فشار متوقف می شود و برای مدتی فشار خرید متوقف می شود و پس از آن **تریندبار
  صعودی** پیدا می شود و احتمال شروع روند (ادامه روند) را زیاد می کند»
  ("PRESSURE GAP: when after **10 to 30 candles** of trend pressure, the
  pressure pauses — buying pressure stops for a while — and then a **bullish
  trend-bar** appears, raising the probability of trend start
  (continuation).")
- Authority: PRIMARY SOURCE. Confidence: HIGH (slide text fully legible).
- Confirms: P-Gap is defined **contextually/developmentally**.
- Does NOT confirm: any OHLC gap formula, endpoint fields, candle indexing,
  the bearish mirror wording (text is buy/bullish-worded while chart demos
  are bearish — the mirror is never explicitly stated), or a deterministic
  detector.

### G-05 — Exhaustion-gap definition = E-GAP (text slide + chart)

- Location: ~25:00 (definition slide, frame `g_1500`); chart example ~27:00
  (frame `g_1620`).
- Exact visible text: «**گپ خستگی** — فشار خرید در **۱۰ یا بیشتر از ۱۰
  کندل** ادامه خواهد داشت… در نواحی نزدیک به مقاومت یک کانتکست خوب برای یک
  پولبک بزرگ تشکیل می شود… قیمت بعد از این گپ برگشت خواهد خورد»
  (buying pressure lasting 10+ candles, near resistance → good context for a
  large pullback; price reverses after this gap.)
- Authority: PRIMARY SOURCE. Confidence: HIGH.
- Confirms: E-GAP identity and its **opposite expectation** (reversal)
  versus P-Gap (continuation) — this is *why* the two differ.

### G-06 — Pressure-gap marking convention (worked charts only)

- Locations: ~23:00–24:45 (frames `g_1380`, `p_1395`–`p_1485`).
- Visual: blue rectangles marking **multi-candle compression zones preceding
  impulsive breakdowns** (bearish demos); red pen traces the breakdown
  candles.
- Authority: PRIMARY SOURCE. Confidence: MEDIUM (marking convention) / LOW
  (semantics).
- Confirms: pressure gap is presented as a *pre-move compression/pause
  zone*, not an inter-candle vacuum.
- Does NOT confirm: zone-boundary rule, box candle count, entry, trigger,
  or SL of any kind.

### G-07 — Gap-trade management rules (text slide; management, not geometry)

- Location: ~11:00 (frame `g_660`).
- Exact visible text (paraphrase-safe, fully legible): a 60%
  correct-prediction state after gap creation permits scalping at 1:1; an
  unknown direction after breakout requires 1:2.
- Authority: PRIMARY SOURCE. Confidence: HIGH (text).
- Confirms: risk-management context only. No geometry.

### G-08 — Common-gap («گپ عادی») section exists

- Location: ~29:00 (frame `g_1740`; definition slide not sampled).
- Authority: PRIMARY SOURCE. Confidence: LOW (existence only).

---

## 3. What P-Gap now means according to the author

Consolidating G-02, G-04, G-05, and G-06 — and only what the slides state:

1. **P-Gap is «گپ فشار» (pressure gap)**, one of four gap types
   (breakout, pressure, exhaustion, common).
2. **It is a developmental pattern, not a candle formula**: 10–30 candles
   of trend pressure → pressure pauses for a while → a trend-bar appears →
   probability of trend start/continuation rises.
3. **It differs from E-Gap («خستگی») by location and expectation**:
   exhaustion follows 10+ candles of pressure near resistance and expects
   reversal/pullback; pressure follows a pause and expects continuation.
4. **Visually it is taught as a pre-move compression zone** (blue boxes),
   not as a measured inter-candle vacuum.
5. The generic gap-detection convention (high[−2] vs low[0] distance,
   bearish) exists in the same video but is **not labeled as P-Gap
   specific**.

No slide in the sampled frames gives P-Gap OHLC endpoints, wick/body
semantics, candle indexing, a bearish-mirror statement, or a formula.

---

## 4. What changed from previous P-Gap status

Previous status (per `SP2L_PGAP_FINAL_SOURCE_BOUNDARY_AUDIT_2026-09-19.md`
and the F10/F11/F12/F14 gap matrix): P-Gap/E-Gap distinction and breakout
relationship supported from the SP2L video; exact OHLC formula unresolved;
P-Gap **UNRESOLVED** as a detector input.

Changes recorded by this document:

| Dimension | Before | After |
|---|---|---|
| P-Gap identity | P-Gap vs E-Gap distinguished (SP2L video) | **P = «فشار», E = «خستگی»** in the author's own 4-type taxonomy (G-02) — SOURCE-CONFIRMED |
| P-Gap definition | none beyond distinction + breakout association | **Contextual definition**: 10–30 candles pressure → pause → trend-bar → continuation likely (G-04) — SOURCE-CONFIRMED as concept |
| E-Gap definition | distinction only | **Contextual definition**: 10+ candles + near resistance → reversal/pullback expected (G-05) — SOURCE-CONFIRMED as concept |
| Why they differ | unsupported beyond "different" | Opposite location + opposite expectation (G-04 vs G-05) — SOURCE-CONFIRMED |
| Generic gap detection | absent | high[−2] vs low[0] distance convention, bearish, type-unspecified (G-01) — SOURCE-SUPPORTED, not P-Gap specific |
| Executable P-Gap geometry | unresolved | **still unresolved** — no formula, endpoints, indexing, or mirror |

Net: the *concept* level is substantially resolved; the *detector* level is
untouched. This reframes the blocker: the missing item is no longer "any
definition" but "an executable OHLC/index detector for a pattern the author
defines developmentally."

---

## 5. What remains unresolved

1. P-Gap OHLC endpoints (high/low/body/wick) — nothing in either video.
2. P-Gap candle indexing for detector purposes — the 10–30 count is a
   developmental window, not anchor indices; the high[−2]/low[0] convention
   is generic, bearish-only, and type-unlabeled.
3. Bullish/bearish mirror statement — never explicitly given for pressure
   gap (text bullish-worded, demos bearish).
4. Per-type candle structure distinguishing pressure gaps from other gaps
   at detection time.
5. Any deterministic P-Gap classification boundary usable in code.
6. Audio content of the gap video (unaudited — stated limitation; slide
   text carries the findings above independently).

---

## 6. Impact on Frozen Geometry

**STILL_BLOCKED.** The gap video upgrades P-Gap concept evidence to
SOURCE-CONFIRMED but contributes zero executable geometry. Per the
governing rule (concept status ≠ geometry status), no blocker moves to
READY and nothing is promoted toward the freeze. The missing-evidence
requirements from prior P-Gap boundary audits stand unchanged.

## 7. Impact on existing P-Gap implementation (implementation-only, not canonical)

`src/domain/strategy-a/PGAPResearch.ts` implements a generic 3-candle
imbalance check (research observation layer, explicitly non-canonical).

Assessment against the gap-video source:

- The author's P-Gap is a **10–30-candle developmental pattern**
  (pressure → pause → trend-bar). A 3-candle imbalance check does not
  represent this pattern and is **not supported by either video**.
- The generic high[−2]/low[0] distance convention (G-01) is the closest
  source-backed detection fragment, but it is type-unspecified and
  bearish-only — it cannot be adopted as "the P-Gap formula" without
  inventing the missing type binding and mirror.
- Therefore the existing implementation remains **IMPLEMENTATION ONLY**:
  it must not be cited as P-Gap evidence, must not be treated as
  source-derived, and must not feed any frozen-geometry claim. No code
  change is made by this document; any future alignment work is out of
  scope here.

---

## Frame inventory (provenance)

29 frames, out-of-repo temp dir (`sp2l-audit/gap`, retained for reuse; not
committed). Survey: `g_60`–`g_1860` every ~120s (16 frames). Pressure-gap
detail: `p_1395`–`p_1485` (7 frames). Breakout/definition detail:
`q_1180`–`q_1360` (6 frames). Key definition slides: `q_1200` (breakout
gap), `q_1340`/`q_1360` (pressure gap), `g_1500` (exhaustion gap),
`g_1020` (detection convention), `q_1180`/`g_1860` (taxonomy).
