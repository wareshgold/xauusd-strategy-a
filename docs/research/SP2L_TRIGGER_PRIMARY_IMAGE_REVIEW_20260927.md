# SP2L Trigger Primary-Image Review — 2026-09-27

## Evidence reviewed

The current official SP2L page contains an author-published chart image titled as an example of SP2L entry, stop-loss and take-profit structure. The page links this image directly from the SP2L strategy section. citeturn1view0

The same official page states:
- after the Spike, the market makes a correction;
- in an uptrend, the corrective candle should hit/reach the Low of the previous candle;
- in a downtrend, the corrective candle should hit/reach the High of the previous candle;
- after the Second Leg is triggered, entry follows the Spike direction. citeturn1view0

The page also links the full SP2L instructional video hosted on YouTube. citeturn1view0

## Image-level finding

The official chart is useful primary evidence because it visually shows the Spike/correction/continuation structure and explicitly labels Entry, SL, TP1 and TP2. However, the published static image does not provide candle indices, timestamps, or an explicit annotation saying which candle is the "previous candle" for the trigger. citeturn2view0

Therefore the image does not uniquely distinguish:

- immediate correction candle versus a later correction candle;
- exact equality/touch versus penetration;
- the precise OHLC index corresponding to "previous candle".

## Video evidence status

The official page exposes the full instructional video link, but the currently accessible web retrieval did not expose a reliable transcript or frame-by-frame content from that video. Therefore no spoken/video claim is promoted into canonical geometry on the basis of inaccessible content.

## Decision

Primary-source evidence now confirms the conceptual sequence:

Spike → correction candle → reach previous-candle Low/High → Second Leg / entry.

But the exact machine-readable trigger indexing remains unresolved.

We therefore do NOT freeze:
- immediate-only scanning;
- scan-forward scanning;
- exact touch equality;
- penetration;
- close-based acceptance.

The executable T1–T6 matrix remains diagnostic only.

## Next evidence target

Obtain primary-source visual or textual evidence that explicitly labels the candle sequence around the trigger, preferably:
1. an annotated chart from the author showing the previous candle and correction candle; or
2. a transcript/frame from the author's full SP2L video that explicitly defines the trigger sequence.

Until then, Frozen Geometry remains blocked.
