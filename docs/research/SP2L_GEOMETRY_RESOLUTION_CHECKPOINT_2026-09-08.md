# SP2L Geometry Resolution Checkpoint

**Date:** 2026-09-08  
**Branch:** `research/source-resolution-entry-level-v2`  
**Gate:** SOURCE RESOLUTION → geometry investigation  
**Production:** unchanged

## 1. Purpose

This checkpoint records what the uploaded source video now establishes visually and what remains unresolved. It deliberately does **not** promote an inferred geometry into canonical Strategy A.

## 2. Direct visual evidence from the uploaded source video

Source video SHA256:
`ef50f60bb55b388fd18762811f3e4e5173ccc188f77606ea6fe95623806a71d9`

Frame convention: `round(t * 30)` at 30 FPS.

### 36:10–36:25 — Spike/P-Gap slide

The slide visibly contains:

- `SP2L Strategy / Spike - 2Leg`;
- four bullish constructions;
- a red X over the left-most construction;
- three numbered constructions (`1`, `2`, `3`);
- shaded horizontal regions on the accepted constructions;
- printed text `Valid BO = P-Gap`.

This establishes two source-level facts:

1. P-Gap is a **valid-breakout condition/marker**, not merely an optional visual annotation.
2. At least three visually distinct Spike constructions are intentionally accepted by the source, while one visually similar construction is rejected.

It does **not** yet establish the exact OHLC formula for P-Gap.

### 35:15–35:55 — P-Gap annotation

The instructor annotates the accepted examples with candle lows (`L`) and gap-related markings. The shaded regions correspond to the visually identified P-Gap area.

The visual evidence supports a relationship involving candle boundaries and non-overlap, consistent with the transcript explanation that a breakout/follow-through construction can contain a gap. However, the recording does not provide a sufficiently unambiguous machine-readable statement of:

- exact candle indices;
- high-vs-low boundary pairing;
- body-vs-wick treatment;
- whether the gap must be adjacent or can be formed after intermediate candles;
- minimum/maximum gap size;
- tolerance or equality handling.

Therefore **P-Gap formula remains unresolved**.

### 36:25–37:00 — AB=CD

The instructor writes `AB=CD` above the SP2L example. The candle-level teaching context is explicit: the concept is applied at candle level rather than by blindly importing a classical Fibonacci implementation.

This confirms the **equality relationship** but does not uniquely label A, B, C and D as OHLC anchors.

Therefore:

- `AB = CD` concept: source-confirmed;
- A/B/C/D anchor mapping: unresolved;
- equality tolerance: unresolved;
- `entry = C`: **not established**.

### 38:45–39:45 — Pending-limit entry

The teaching diagram visibly shows `BO`, `Limit` / `Buy Limit`, and an SL line. The sequence is drawn as a directional move followed by correction, with the order level already present during the correction.

This directly corroborates the transcript: the instructor says the limit order can be placed within the first three candles, before waiting for a later candle, and that the stop distance is known before activation.

Therefore the canonical execution semantics must remain:

**signal setup → pending limit exists before fill → later price action may fill or invalidate it**

A later close-reclaim trigger is not an equivalent implementation.

### ~62:20–63:00 — Real XAUUSD execution

The real-chart section shows concrete horizontal structural levels and subsequent trade/order outcomes. It confirms that execution is based on explicit price structure rather than an abstract indicator-only event.

The compressed visual material still does not provide a sufficiently explicit A/B/C/D legend to map every marked level deterministically.

Therefore real-chart evidence strengthens the need for structural anchors but does not freeze their formula.

## 3. Geometry decision matrix

| Component | Evidence | Current decision |
|---|---|---|
| Spike is directional movement after range/context | transcript + slide | **confirmed concept** |
| Breakout + follow-through | transcript + slide | **confirmed concept** |
| P-Gap required for valid BO | `Valid BO = P-Gap` + transcript | **confirmed gate** |
| Exact P-Gap formula | visual hints only | **UNRESOLVED** |
| Generic 3-candle imbalance = P-Gap | no direct source proof | **REJECTED as canonical assumption** |
| Spike variants | 3 accepted visual constructions + 1 rejected | **candidate taxonomy; freeze pending fixture mapping** |
| Pending-limit entry | transcript + direct diagram | **confirmed execution semantics** |
| Entry price anchor | visual line + correction language | **not fully frozen** |
| Structural invalidation | transcript + SL diagram | **confirmed concept; exact anchor unresolved** |
| Leg2 magnitude = Leg1 | transcript | **confirmed concept** |
| AB=CD | explicit handwritten label | **confirmed concept** |
| A/B/C/D anchors | no unique labels | **UNRESOLVED** |
| AB=CD tolerance | no source value | **UNRESOLVED** |
| TP1 ≈ 1:1 | transcript explicitly says TP1/1:1 is usual | **strong source evidence** |
| TP2 / 2X | separate management material | **separate module; not merged** |
| Round-number context | transcript gives XAU examples | **context concept supported; exact algorithm unresolved** |

## 4. Important rejection

The following implementation shortcut remains explicitly prohibited:

> `P-Gap = generic three-candle imbalance`

The visual source shows a shaded P-Gap region around accepted breakout constructions, but it does not provide enough evidence to prove that a generic ICT-style three-candle imbalance is the intended object. Implementing that formula would convert an interpretation into a canonical rule without source confirmation.

## 5. Synthetic fixtures required before freeze

The next fixture set should contain deliberately discriminating candle sequences for:

1. breakout + immediate non-overlap;
2. higher-lows first, then P-Gap;
3. accepted third construction where the following candle does not extend the preceding low/high as described by the source;
4. rejected channel/overlap construction;
5. equal boundary case (touch but no strict gap);
6. wick-only separation;
7. body-only separation;
8. gap appearing one candle after the initial breakout;
9. correction crossing the first structural low/high;
10. pending order placed before fill versus close-reclaim after correction.

Each fixture must record competing interpretations and expected classification from the source evidence. No historical performance may be used to select the interpretation.

## 6. Current gate state

**SOURCE SEMANTICS:** materially resolved  
**P-GAP GEOMETRY:** unresolved  
**ENTRY SEMANTICS:** materially resolved; exact price anchor still needs freeze  
**A/B/C/D:** unresolved  
**AB=CD TOLERANCE:** unresolved  
**SYNTHETIC FIXTURES:** next gate  
**FROZEN GEOMETRY:** blocked  
**DEV / VAL / HOLDOUT:** not authorized  
**PRODUCTION:** unchanged

## 7. Research consequence

The evidence is now strong enough to replace the old conceptual ambiguity around entry semantics, but **not** strong enough to produce a canonical historical trade stream. The correct next step is to build and execute the discriminating synthetic fixture suite against competing P-Gap and anchor hypotheses, then return only source-supported interpretations to the frozen specification.
