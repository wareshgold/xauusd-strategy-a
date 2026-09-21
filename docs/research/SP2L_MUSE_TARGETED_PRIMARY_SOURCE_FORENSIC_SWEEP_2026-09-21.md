# MUSE Targeted Primary-Source Forensic Sweep — 2026-09-21

## Mission
Run one final full-video forensic sweep against the original SP2L teacher video. Review ONLY unresolved executable questions. Do not infer rules from implementation, backtests, synthetic fixtures, author replicas, or trading outcomes.

## Evidence standard
A finding is promotable only when the video provides enough evidence to specify the executable rule: exact timestamp; frame/screenshot reference when visual; exact on-screen text or faithful explicitly marked audio paraphrase; candle/price-field identity; indexing/order; boundary/threshold; event semantics; direction and precedence where relevant.

## Do NOT repeat
Do not re-audit F10/F11/F12 evidence already closed in existing forensic reports unless a genuinely different timestamp/statement is found.

## Target questions

### F09 — Entry
Find explicit evidence for Entry price field, exact candle/index, reference level, update behavior, and precedence.

### F12 — Trigger / Activation
Find explicit trigger condition, candle role/index, touch/breach/close semantics, trigger-vs-activation-vs-fill distinction, 1/2/3-candle mapping, and precedence.

### F15 — Bearish mirror
Search specifically for explicit Sell Limit, bearish trigger, activation, deletion/replacement, and bearish candle/index geometry. Synthetic symmetry is not evidence.

### F13 — 2X
Search specifically for numeric/geometric binding of 2X to target, TP1, TP2, Entry-to-SL, AB=CD, half-target, percentage, or R multiple. Do not infer 50% from label position.

### P-Gap — executable construction
Search for explicit pressure/compression boundaries, gap endpoints, OHLC fields, indexing/order, threshold/buffer, bullish formula, bearish mirror, and relation to order-space/BO. Do not import formulas from a separate gap video unless explicitly adopted here.

### F08 — swing selection
Search for explicit universal swing definition, lookback, indexing, tie-break, latest-vs-original reference, and HL/LH selection. A worked example is not a universal algorithm.

### F14 — AB=CD
Search only for explicit A/B/C/D anchors, price field, wick/body semantics, D observed/projected, and equality tolerance. The approximate Leg2=Leg1 concept is already source-confirmed.

## Output schema
Return one record per finding with: feature; status (SOURCE_CONFIRMED_EXECUTABLE/PARTIAL/NOT_FOUND); timestamp range; frame reference; exact on-screen text; audio statement; price fields; candle roles; indexing; boundary/threshold; event semantics; direction; precedence; executable rule; confidence; why this is new; source scope PRIMARY_VIDEO_ONLY.

## Hard prohibitions
No guessed formula. No backtest-selected geometry. No optimization-derived tolerance. No implementation-to-source promotion. No looks-like evidence presented as executable. No touch=fill assumption. No trigger=activation/fill assumption. No synthetic bearish symmetry as source evidence. No production BUY/SELL decision.

## Final decision
If no genuinely new executable evidence is found, return: NO_NEW_EXECUTABLE_PRIMARY_SOURCE_EVIDENCE. State that the blocker boundary remains final until new primary-source material/evidence is obtained.

## Existing evidence context
Use the repository's existing F08/F10/F11/F12/F13/F14/P-Gap forensic closure documents to avoid repeating already-audited evidence. The goal is gap closure, not another generic video summary.