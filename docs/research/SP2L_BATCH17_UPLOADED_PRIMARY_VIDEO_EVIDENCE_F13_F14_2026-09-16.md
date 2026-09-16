# SP2L Batch 17 — Uploaded Primary Video Evidence — F13/F14 — 2026-09-16

## Artifact

User-provided local video artifact:
`strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Measured duration: approximately 4155.72 seconds (69m 15.72s).

The file contains H.264 video and AAC audio streams. No separate subtitle stream is exposed by ffprobe; therefore this batch uses direct visual evidence from the supplied primary artifact rather than claiming a recovered subtitle transcript.

## F14 — AB=CD

### Direct visual evidence

Around 37:00–37:25 (approximately 2220–2240 seconds), the SP2L training slide explicitly displays the handwritten label `AB=CD` above the SP2L diagram. The same slide also shows the SP2L branding and the P-Gap example.

This is direct evidence from the supplied training artifact that AB=CD is not merely a secondary-source interpretation; the concept is explicitly taught in the artifact.

### What this resolves

- AB=CD / equal-leg concept: **PRIMARY-ARTIFACT CONFIRMED**.

### What remains unresolved

The supplied video frames reviewed in this batch do not uniquely specify:

- A anchor selection;
- B anchor selection;
- C anchor selection;
- D anchor selection;
- wick vs body vs open/close semantics;
- whether D is projected or observed;
- tolerance/ratio semantics;
- numeric tolerance or rounding;
- exact candle-selection algorithm.

Therefore no deterministic AB=CD geometry is frozen.

## F13 — 2X

### Direct visual evidence

Around 38:20–38:50 (approximately 2300–2330 seconds), the training diagram explicitly annotates `2X` alongside the SP2L setup.

Around 42:00–42:35 (approximately 2520–2555 seconds), a dedicated diagram labels `Buy`, `2X`, and `SL` on three horizontal levels. The drawing uses vertical distance markers between these levels and visually places the 2X level between the initial Buy/Entry level and SL, consistent with the previously observed 50%-distance concept.

Around 42:40–43:20 (approximately 2560–2600 seconds), the same teaching sequence labels `TP1`, `TP2`, `Entry`, and `SL`, providing direct primary-artifact evidence for the existence of the two target levels and the entry/stop reference diagram.

### What this resolves

- 2X concept: **PRIMARY-ARTIFACT CONFIRMED**.
- The artifact provides direct visual support for an intermediate 2X level between Entry/Buy and SL.
- The visual construction is consistent with the 50%-distance concept already documented from author-associated material.

### What remains unresolved

The artifact review in this batch does not provide a sufficiently explicit numeric statement that can be safely promoted to a canonical executable formula, nor does it uniquely resolve:

- exact activation condition for 2X;
- whether 2X is a pending order, re-entry, or another order type in every case;
- fill semantics;
- replacement/cancellation behavior;
- position sizing semantics;
- interaction with an already-filled initial Entry;
- exact timing relative to the trigger candle.

Therefore `2X = 50% of Entry→SL` remains **source-supported conceptually but not frozen as a complete executable rule**.

## Evidence discipline

This batch uses the user-supplied primary training artifact and does not use backtest performance to choose among interpretations. No production rule, variant, or 125R artifact was modified.

## Gate consequence

F13: **PRIMARY-ARTIFACT CONFIRMED CONCEPT / EXECUTION SEMANTICS UNRESOLVED**.

F14: **PRIMARY-ARTIFACT CONFIRMED AB=CD CONCEPT / ANCHORS AND TOLERANCE UNRESOLVED**.

Frozen Geometry remains BLOCKED.
