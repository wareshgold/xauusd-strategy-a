# SP2L G214 — 2x Midpoint Corroboration and Order-State Correction

Date: 2026-09-10  
Scope: source-resolution research only. No executable geometry is frozen.

## 1. Direct order-panel correction

Direct inspection of the supplied MP4 around 21:40 (frame `round(1300×30)=39,000`) shows multiple terminal rows. At that exact state:

- row 1: Price `3229.08`, S/L `3237.12`, T/P `0.00`
- row 2: Price `3223.84`, S/L `3235.50`, T/P `3213.33`
- row 3: Price `3228.88`, S/L `3235.50`, T/P `0.00`

Therefore the earlier G213 statement that the first row already had TP `3213.44` at 21:40 was incorrect. Later frames show the first row with TP `3213.44`; this is a later order-state change.

## 2. Strong candidate relationship for `2x`

For the later state with:

- Entry/Price = `3229.08`
- SL = `3237.12`

risk distance is `8.04`.

The midpoint between Entry and SL is:

`3229.08 + (3237.12 - 3229.08)/2 = 3233.10`

The chart's `2x` reference line is visually located around this midpoint. This makes the following interpretation a strong candidate:

`2x = Entry + 0.5 × (SL − Entry)` for a short setup,

with the bearish mirror for a long setup.

This is **not frozen** yet.

## 3. Independent authoritative corroboration

The official creator site describes a secondary entry at **50% of the distance from Entry to Stop-Loss**. It also states that, in bullish SP2L, the corrective candle waits to reach the low of the previous candle, mirrored for bearish setups, and that SL is placed behind the candle from which the Spike originated. citeturn6search0turn6search1

The public source index also explicitly lists `نحوه و دلیل ورود در 2x` (how/why to enter at 2x) and later `آموزش دقیق ۴ معامله ی ابتدای ویدیو` (detailed teaching of the four initial trades), corroborating that `2x` and the four-trade execution are deliberate teaching topics. citeturn0search0turn1view0

## 4. Interpretation boundary

This evidence does **not** yet prove:

- that the primary pending-limit Entry is always `E`;
- that `2x` is universally exactly 50% Entry→SL;
- that the source's `2x` is identical to a generic Fibonacci concept;
- that the terminal Price field equals geometric C;
- that TP is universally 1R, 2R, or level `2`;
- exact candle indexing or wick/body treatment for SL;
- pending-order replacement/cancellation semantics.

The official webpage is corroborative source material, not a substitute for unresolved raw-video geometry.

## 5. Audio/subtitle recovery status

The supplied MP4 has video + AAC audio but no embedded subtitle stream. The available local environment has no installed Whisper/faster-whisper model/package, and the YouTube timed-text endpoint could not be retrieved through the available web interface. Public Telegram indexing confirms that a Persian subtitle version was prepared/distributed, but the actual subtitle text was not exposed in the retrieved page. citeturn1view0turn3search0

Therefore no transcript is fabricated or treated as source evidence.

## 6. Gate decision

**SOURCE RESOLUTION remains BLOCKED at executable geometry.**

New status:

- `2x` midpoint relationship: **STRONG CANDIDATE / SOURCE-CORRELATED — NOT FROZEN**
- 50% secondary-entry concept: **official-source corroborated**
- exact primary Entry anchor: **UNRESOLVED**
- exact SL geometry: **UNRESOLVED**
- exact TP/Leg2 geometry: **UNRESOLVED**
- audio/transcript: **not recovered with sufficient provenance**
