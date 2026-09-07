# G4/G5 Visual-Frame Extraction Request

**Date:** 2026-09-07
**Branch:** `research/phase29-d-archetype-residual-after-geometry`
**Purpose:** Exact list of chart coordinates to extract from the Poorsamadi SP2L video so G4 (Leg 1 endpoints) and G5 (Leg 2 origin) can be frozen with source provenance.
**Video:** https://youtu.be/7HEC5mO3d3U (SP2L lesson, ~1:09:16)

This request exists because the preserved transcript establishes the semantics but not the machine-readable OHLC coordinates. The transcript quotes below are from `docs/strategy/source/POORSAMADI_SP2L_SOURCE.txt`. Every coordinate we need is something the teacher points at or names on the chart — nothing is inferred.

---

## 1. General capture instructions

For **every** point listed below, please provide:

1. A **screenshot of the exact frame** where the teacher's cursor/pointer/arrow is on the point (or the clearest adjacent frame if the pointer flickers).
2. The **candle date + time** of that point exactly as shown on the chart (note the clock in the corner of the chart, if visible).
3. The **price** the point refers to, and **which OHLC element** it is: candle high / candle low / close / open / horizontal level line (a level is not necessarily a candle extreme — say so if it looks like a drawn level).
4. The **chart timeframe** shown in the video at that moment (the teacher mentions M1 or M5 — confirm which one each segment uses).
5. Whether the sequence is a **BUY or SELL** scenario in that segment.

The video clock is `mm:ss` / `h:mm:ss`; please match the exact second as close as possible.

## 2. Do NOT re-extract

- The **37:22 level-break + gap frame** is already supplied and recorded in the source evidence register (`LEVEL BREAK + GAP can occur in the same transition/event`). It does not need to be requested again.

---

## 3. Segment 1 — 36:59–37:08 (spike → correction → Leg 2 equality)

Transcript (36:59): *"وقتی که یک اسپایک داریم، انتظار داریم این یک اصلاح به ما بده و بره لگ دومش رو کامل بکنه که لگ اول با لگ دوم برابری میکنه."*
(When we have a spike, we expect it to give a correction and complete its second leg, with Leg 1 equal to Leg 2.)

| ID | What we need | Why (gate) |
|---|---|---|
| S1-A | The **start of Leg 1** — the chart point the teacher treats as the beginning of the measured first leg. | G4 |
| S1-B | The **end of Leg 1** — where the first leg is considered complete (spike extreme?). | G4 |
| S1-C | The **correction extreme** — the deepest point of the correction between the legs. | G5 |
| S1-D | The **Leg 2 completion / target** — where Leg 2 "completes" per the equality statement. | G6 |

## 4. Segment 2 — 1:02:41–1:03:32 (outer leg vs nested leg; deep correction)

Transcript (1:02:41): *"...یک سقفی داشتیم اینجا اومده سقف پایین تر، سقف پایین تر، سقف پایین تر عملا چهار تا سقف پایین تر در جهت این روند قبلی ساخته."*
(1:02:52) *"من دنبال لگ دوم این بودم... این لگ اولش بوده، اگر از اینجا بگیریم، لگ دومش میشه اینجا، این لگ رو من منتظرش بودم."*
(1:03:03) *"حالا این لگ خودش برای خودش یک 2Leg داشته تو خودش... عملا تی پی من اینجا خورده بود."*
(1:03:19) *"سناریوی اصلیم اینه که اینو کلا یک لگ و این کلا یک لگ و از اصلاحش که خیلی عمیق بود، میشه از اینجا تا اینجا لگ بعدیشه."*

| ID | What we need | Why (gate) |
|---|---|---|
| S2-1 | The **four "lower high" points** he counts (سقف پایینتر ×4) — each candle time + price, and whether each is a wick high or body high. | G1 (structural LH sequence) |
| S2-2 | **Parent Leg 1 start** — the chart location "این لگ اولش بوده". | G4 |
| S2-3 | **Parent Leg 1 end** — where that first segment ends. | G4 |
| S2-4 | The **"از اینجا" point** for Leg 2 — where he says "if we take it from here, Leg 2 is here". This is a primary **C origin candidate**. | G5 |
| S2-5 | The **deep-correction origin** — "از اصلاحش که خیلی عمیق بود، میشه از اینجا" — the exact chart point the teacher starts the next leg from. | G5 |
| S2-6 | The **parent Leg 2 end** — "رسیدم به رأس لگ بعدیش". | G6 |
| S2-7 | The **nested 2Leg TP** — "تی پی من اینجا خورده بود" (the inner structure's own target). | nested-leg disambiguation |

## 5. Segment 3 — 1:04:00–1:04:32 (deep leg, order placement, Leg 1 definition, TP1)

Transcript (1:04:00): *"اگر میخواستی اینجا ها دو دل بوده باشی میایم صبر میکنیم تا جایی که یک لگ عمیق ببینی، ببینید لگ عمیق من از کجا شروع شده؟ از اینجا."*
(1:04:10) *"سقف پایین تر، سقف پایین تر، سقف پایین تر، سقف پایین تر، سقف پایین تر، ۷ تا سقف پایین تر."*
(1:04:19) *"و میام این اوردرم رو میزارم اینجا و میکشم پایین، میکشم پایین... تا اینجا فعال بشه و عملا لگ اول من که از اینجا تا اینجا بوده SP2Leg من میشه اینجا."*
(1:04:32) *"یعنی تی پی این پوزیشن اینجا بوده برای ریوارد یک."*

| ID | What we need | Why (gate) |
|---|---|---|
| S3-A | **Deep leg start** — the point he points at for "لگ عمیق من از کجا شروع شده؟ از اینجا". This is the most important single coordinate: the primary **C origin** of the parent scenario. | G5 |
| S3-1..7 | All **seven "lower high" points** he counts (سقف پایینتر ×7) — time + price each, wick vs body. | G1 (structural LH sequence) |
| S3-B | **Leg 1 start** — "لگ اول من که از اینجا تا اینجا بوده": the first "از اینجا". | G4 |
| S3-C | **Leg 1 end** — the second "تا اینجا" of the same sentence. | G4 |
| S3-D | **Pending-limit placement price** — "اوردرم رو میزارم اینجا" (the level where the order was first placed). | G2 (pending-limit level) |
| S3-E | **Activation level** — "میکشم پایین... تا اینجا فعال بشه" (the price where the dragged order got filled). | G2 / G5 fill-vs-C distinction |
| S3-F | **TP1 price** — "تی پی این پوزیشن اینجا بوده برای ریوارد یک". | G6 / TP1 projection |

## 6. The critical G4/G5 discriminations this request resolves

1. **G4 (Leg 1 endpoints):** whether the teacher's Leg 1 A→B is (a) structural point → structural point, (b) spike start → spike extreme, (c) breakout level → spike extreme, or (d) relevant-candle open → spike extreme. The S1-A/B, S2-2/3 and S3-B/C coordinates answer this.
2. **G5 (Leg 2 origin C):** whether the teacher's Leg 2 start is (a) the correction extreme, (b) a structural LH/HL price, (c) the pending-limit price, or (d) the actual fill. The S2-4/5 and S3-A/D/E coordinates answer this — S3-A vs S3-D vs S3-E being the decisive triple.
3. **Fill ≠ C:** if the activation price (S3-E) differs from the deep-leg start (S3-A), that difference is explicit source evidence that `fillPrice` is not the geometric `C`.

## 7. Coordinate delivery sheet (fill in per point)

| Point ID | Video time | Candle date | Candle time | Price | OHLC element (high/low/close/level) | Chart TF | BUY/SELL | Notes |
|---|---|---|---|---|---|---|---|---|
| S1-A | | | | | | | | |
| S1-B | | | | | | | | |
| S1-C | | | | | | | | |
| S1-D | | | | | | | | |
| S2-1..S2-4 | | | | | | | | |
| S2-5 | | | | | | | | |
| S2-6 | | | | | | | | |
| S2-7 | | | | | | | | |
| S3-A | | | | | | | | |
| S3-1..S3-7 | | | | | | | | |
| S3-B | | | | | | | | |
| S3-C | | | | | | | | |
| S3-D | | | | | | | | |
| S3-E | | | | | | | | |
| S3-F | | | | | | | | |

## 8. Guardrails (how the data will be used)

- The extracted coordinates will be recorded as **source-visual evidence with provenance** (video time, frame, OHLC element) and used to freeze G4/G5 candidate geometry and build deterministic synthetic fixtures.
- No coordinate will be adjusted, rounded, or "repaired" to fit the existing baseline.
- Historical performance will not be used to choose between candidate interpretations of the coordinates.
- If a point cannot be read from the frames (blur, pointer off-screen), report it as **UNREADABLE** rather than estimating — we will re-request that single point only.