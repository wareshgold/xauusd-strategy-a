# SP2L Transcript Cross-Resolution — 2026-09-14

## Status

RESEARCH-ONLY. No canonical geometry promotion. No engine changes. No execution-rule invention. Source meaning outranks backtest performance.

## Tier-1 transcript artifact

Authoritative uploaded transcript: `پورصمدیSP2L TRANSCIBE.txt`.

The transcript explicitly requires candle-by-candle reading and states that each candle's high/close/open/low must be read sequentially; this is a source constraint against replacing the source geometry with a coarse wave abstraction.

## Cross-resolution findings

### F8/F9 — Entry correction and Leg-2 separation

At 38:38 the source describes the next candle beginning correction and defines the correction semantically as moving below the first low. At 38:53–39:11 it describes a gap/breakout/follow-through sequence and says the limit order can be placed during the first three candles rather than waiting for another candle. At 39:26 the source states that the distance to SL is already defined because a return to the cited level invalidates the scenario. At 39:48–40:16 the source allows deleting/replacing the pending order when a later candle forms, but also describes retaining/moving the order when the distance is not large enough to damage money management.

Decision: semantic entry and pending-order behavior are confirmed; exact executable entry price anchor and deterministic retain/replace threshold remain unresolved.

### F10 — Structural invalidation / SL

The source explicitly links invalidation to price returning to the lower structural level and separately discusses SL placement. However, the transcript does not uniquely specify the exact OHLC/wick/body boundary that an engine must use.

Decision: structural invalidation is source-supported; exact OHLC boundary remains unresolved.

### F11 — Pending-order refresh

The source explicitly describes a later candle causing a possible delete/replacement of the pending order, followed by a discretionary retention example when the new distance is not sufficiently large to impair money management.

Decision: structure-dependent refresh semantics confirmed; deterministic threshold/algorithm not source-discriminated.

### F12 — Trigger family

The source presents multiple constructions and explicitly discusses one-, two-, and three-candle trend/trigger cases. The limit order may be placed within the first three candles in the described setup.

Decision: 1/2/3-candle family confirmed; exact acceptance classifier remains unresolved.

### P-GAP / Breakout

At 31:02–31:55 the source defines breakout using a close followed by a follow-through candle that does not return/overlap into the prior area, and identifies P-GAP as a simple sign of the breakout while explicitly distinguishing P-GAP from E-GAP. At 33:51–34:14 the source again connects breakout + follow-through and P-GAP with the strong trend/spike construction.

Decision: breakout/follow-through/P-GAP semantics confirmed. Exact P-GAP OHLC formula, candle indices, and invariants are not uniquely specified by transcript + currently registered frame evidence. Do not substitute a generic three-candle imbalance formula.

### F14 — AB=CD / Leg-2 projection

At 37:57 the source says that after the increase/correction it expects the next leg to be built to the same size as the preceding leg. Other transcript sections show 2X and target examples, but do not uniquely specify the executable A/B/C/D anchors or equality tolerance.

Decision: `Leg2Magnitude ≈ Leg1Magnitude` is source-supported as a semantic concept; A/B/C/D anchor definitions and tolerance remain unresolved.

### F13 — 2X / TP1 / TP2

The transcript explicitly references 2X and separately discusses TP1/TP2. It also describes target-taking and later examples reaching 2X and beyond. These observations establish source-level target concepts, not a unique executable formula for TP1/TP2/2X.

Decision: existence/semantics confirmed; exact executable formulas remain unresolved.

### F15 — Bearish mirror

The transcript contains bearish structural examples, including lower-high sequences and sell execution/SL examples. However, the available text does not uniquely establish that every bullish geometric rule has an exact deterministic sign-inverted bearish counterpart, including all candle anchors and invalidation semantics.

Decision: bearish examples confirmed; deterministic mirror remains unresolved.

## Video-frame cross-check window

Previously registered direct frame evidence covers:

- 36:59–37:22: visual association of Valid BO = P-Gap and AB=CD.
- 38:40–39:50: visual Buy Limit execution and separate SL representation.
- 1:02:41–1:03:32: bearish structural example.
- 1:04:00–1:04:32: bearish order/continuation sequence.

The transcript strengthens the semantic interpretation of these windows but does not eliminate the remaining geometric ambiguities. In particular, the transcript itself repeatedly emphasizes candle-by-candle interpretation, while the visuals do not provide enough unambiguous numerical/candle-index information to derive the exact engine formulas.

## Canonicalization gate

No remaining dimension is promoted to canonical executable geometry from this pass.

### Current gate

| Dimension | Source status | Executable status |
|---|---|---|
| Breakout / follow-through | Confirmed | Exact indexing still unresolved |
| P-GAP | Confirmed concept | Formula/indexing unresolved |
| Entry correction | Confirmed concept | Exact price anchor unresolved |
| Leg-2 start | Semantically separated | Exact endpoint unresolved |
| Structural invalidation | Confirmed concept | Exact OHLC boundary unresolved |
| Pending refresh | Confirmed behavior | Deterministic threshold unresolved |
| 1/2/3-candle trigger family | Confirmed | Classifier unresolved |
| AB=CD | Magnitude relation supported | A/B/C/D + tolerance unresolved |
| 2X / TP1 / TP2 | Concepts/examples confirmed | Formula unresolved |
| Bearish mirror | Examples confirmed | Deterministic mirror unresolved |

## Governance conclusion

This transcript cross-resolution pass materially strengthens the source evidence but does **not** satisfy the canonicalization gate. The correct next action is not to optimize or backtest competing geometry hypotheses. The remaining hypotheses must stay explicitly unresolved until Tier-1/2 evidence discriminates them and the geometry is manually approved for canonicalization.
