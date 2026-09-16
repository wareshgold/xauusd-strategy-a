# SP2L Batch 18 — Primary Artifact Forensic Pass — F8/F9/F10/F11/F12/F15 — 2026-09-16

## Scope

Forensic review of the user-supplied primary SP2L training video:
`strtjy_sp2l_strategy_subtitle_7hec5mo3d3u_7899aa08.mp4`

Measured duration: approximately 4155.72 s (69m 15.72s).

This pass inspects visible teaching diagrams/examples around the relevant sections. It records only what the artifact visibly establishes; it does not infer hidden OHLC semantics or convert drawings into executable code.

## F8 — First important swing / evolving swing

### Direct artifact observations

Around 26:00–29:00 (approximately 1560–1740 s), the training material repeatedly illustrates bullish candle sequences and marks lower points/levels on candles while discussing the structure. Around 30:00 (1800 s), the material connects the examples to entry/TP/SL concepts.

### Resolution

The artifact strengthens that local candle lows/levels are visually relevant to bullish SP2L structure. It does **not** uniquely specify an algorithm for choosing the "first important" swing versus an evolving/latest swing when multiple candidates exist.

Status: **PRIMARY-ARTIFACT EVIDENCE STRENGTHENED / SELECTION ALGORITHM UNRESOLVED**.

## F9 — Entry vs Leg-2 start

### Direct artifact observations

Around 39:30–41:00 (approximately 2370–2460 s), the training sequence shows a horizontal level associated with `Buy Limit`, then subsequent diagrams discuss order handling and deletion. Around 42:00–43:20 (approximately 2520–2600 s), the dedicated setup diagram labels separate horizontal levels as `Buy`, `2X`, `TP1`, `TP2`, `Entry`, and `SL`.

### Resolution

The artifact directly supports that an order/entry level is represented as a distinct horizontal price level and that Leg-2/entry/target concepts are taught separately. It does **not** uniquely establish an exact candle timestamp, touch/break/close activation rule, or an `Entry = C` mapping.

Status: **PRIMARY-ARTIFACT EVIDENCE STRENGTHENED / EXACT ACTIVATION SEMANTICS UNRESOLVED**.

## F10 — Structural invalidation vs SL price semantics

### Direct artifact observations

The order-placement teaching around 39:30–41:00 shows a horizontal order level and later discusses deletion/order handling. The dedicated risk diagram around 42:00–43:20 explicitly labels `Entry` and `SL` as separate levels, with SL drawn below the bullish structure.

### Resolution

The artifact confirms that SL is represented as a distinct level below the bullish setup in this example. It does **not** establish whether the canonical boundary is the wick extreme, candle body, open/close, structural swing, or a buffered price; nor does it define invalidation timing.

Status: **PRIMARY-ARTIFACT EVIDENCE STRENGTHENED / EXACT PRICE SEMANTICS UNRESOLVED**.

## F11 — Pending-order lifecycle / replacement

### Direct artifact observations

Around 40:30–41:00 (approximately 2430–2460 s), the diagram visibly includes a `delete` annotation while discussing order/money handling around a horizontal pending level. Around 39:30–40:30 (approximately 2370–2430 s), the material also demonstrates a `Buy Limit` placement.

### Resolution

This is direct evidence that pending-order placement and deletion are discussed in the primary artifact. It is **not enough** to establish a deterministic lifecycle/state machine: the artifact review does not uniquely specify when an older order must be deleted, whether it is replaced by a newer level, what invalidates it, whether expiry exists, or whether multiple pending orders may coexist.

Status: **PRIMARY-ARTIFACT ORDER-LIFECYCLE EVIDENCE / REPLACEMENT RULE UNRESOLVED**.

## F12 — Trigger taxonomy

### Direct artifact observations

Around 36:00–38:00 (approximately 2160–2280 s), the training material shows bullish candle sequences and explicitly combines the SP2L diagram with the text `AB=CD` and a `Valid BO = P-Gap` annotation. Around 39:30–41:00 it demonstrates the order level as a horizontal `Buy Limit` level.

### Resolution

The artifact directly supports a breakout/validation concept and order placement associated with a horizontal level. It does **not** uniquely resolve a canonical 1-, 2-, or 3-candle trigger family, nor whether activation is by intrabar touch, break, bar close, retest, or a combined sequence in all cases.

Status: **PRIMARY-ARTIFACT TRIGGER EVIDENCE STRENGTHENED / EXACT TAXONOMY UNRESOLVED**.

## F15 — Bearish mirror

### Direct artifact observations

The primary artifact contains both bullish and bearish SP2L teaching material and uses directional labels/examples throughout the training. The reviewed artifact frames establish that the strategy is taught as a directional setup rather than a bullish-only construction.

### Resolution

This supports the existence of a bearish counterpart at the conceptual level. The reviewed frames do not uniquely establish that every lower-level execution detail is a strict mathematical mirror of the bullish case, including exact LH selection, High semantics, trigger path, pending-order handling, and SL boundary.

Status: **PRIMARY-ARTIFACT DIRECTIONAL EVIDENCE / EXACT BEARISH EXECUTION GEOMETRY UNRESOLVED**.

## Cross-fixture conclusion

This pass materially improves source evidence for **order placement/deletion (F11), horizontal entry levels (F9), breakout/validation context (F12), and structural level/SL representation (F10)**. It also strengthens the visual evidence that local lows/levels participate in bullish examples (F8).

However, none of these observations uniquely supplies the deterministic executable semantics required for a geometry freeze. The correct action is therefore to preserve the unresolved alternatives rather than selecting one from the drawings.

## Gate decision

- Source Resolution: **PARTIAL PASS — strengthened by primary artifact**
- Frozen Geometry: **BLOCKED**
- Untouched Validation: **LOCKED**
- Robustness/Stability: **LOCKED**
- Fresh Holdout: **LOCKED**
- Production: **OFF**
- 125R: **UNTOUCHED**

## Explicit non-canonical items preserved

- exact swing-selection algorithm;
- exact Entry activation timestamp/price;
- exact SL boundary/buffer;
- pending-order replacement/refresh/expiry state machine;
- exact 1/2/3-candle trigger taxonomy;
- exact bearish mirror geometry;
- AB=CD A/B/C/D anchors and tolerance;
- complete 2X activation/fill semantics.

No backtest variant was selected from this evidence and no production implementation was changed.
