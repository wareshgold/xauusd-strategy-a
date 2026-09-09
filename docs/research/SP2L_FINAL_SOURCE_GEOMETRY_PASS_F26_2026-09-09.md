# SP2L Final Source Geometry Pass — F26 — 2026-09-09

## Scope

Final source-first comparison of the remaining geometry blockers using the primary video, extracted frame evidence, transcript reconstruction, and the bullish/bearish visual examples available in the research record.

## Source decisions

### P-Gap
Confirmed as a first-class source concept and explicitly associated with valid breakout. The source distinguishes P-Gap from E-Gap/Common-Gap and shows more than one construction/event order. The evidence does not uniquely specify an OHLC formula or universal candle indexing rule.

**Decision:** semantic = CONFIRMED; executable geometry = UNRESOLVED.

### Entry
Pending Limit is explicit. The demonstrated bullish sequence shows the pending entry level evolving with the structural higher-low sequence rather than establishing a universal fixed initial-low formula. The bearish visual material supports the directional mirror (Sell Limit around a relevant structural high), but does not uniquely select wick/body/pivot coordinates.

**Decision:** mechanism = CONFIRMED; exact universal anchor = UNRESOLVED.

### Structural invalidation / SL
Entry and SL are visibly separate. The source treats invalidation structurally and discusses order/risk changes when structure changes. Exact wick/body/pivot anchor and any buffer are not uniquely stated.

**Decision:** structural meaning = CONFIRMED; executable OHLC anchor = UNRESOLVED.

### Pending update
The source permits deleting/replacing a pending order when the relevant risk distance changes materially. No deterministic numerical threshold or exact timing rule is source-confirmed.

**Decision:** qualitative behavior = CONFIRMED; threshold/timing = UNRESOLVED.

### Trigger
The source contains one-, two-, and three-candle trigger examples plus key-bar language. These examples establish a trigger family, but do not provide a complete deterministic acceptance/timing taxonomy sufficient to select one formula without interpretation.

**Decision:** family = CONFIRMED; exact acceptance/timing = UNRESOLVED.

### AB=CD / Leg 1 → Leg 2
AB=CD is explicit and describes a magnitude relationship between the legs. The source examples do not uniquely define four OHLC anchors, wick/body convention, or tolerance. Leg 2 is a continuation objective, but the executable projection/TP1 formula remains under-specified.

**Decision:** relationship = CONFIRMED; executable projection = UNRESOLVED.

### Bearish mirror
The available bearish examples support the directional structural mirror: Lower Highs → bearish breakout/P-Gap context → correction → Sell Limit → structural invalidation above → bearish Leg 2. This establishes the abstraction, not a complete bearish OHLC formula.

**Decision:** directional mirror = CONFIRMED; exact bearish geometry = UNRESOLVED.

## Non-equivalences frozen

- P-Gap is not frozen as generic three-candle FVG/imbalance.
- Pending Limit is not replaced by market-close reclaim.
- Entry is not assumed to equal Leg2 start.
- Stop is not derived from risk percentage, ATR, or fixed distance.
- Backtest profitability is not allowed to choose source geometry.
- No AB=CD tolerance is invented.
- No universal wick/body convention is invented.

## Gate decision

**SOURCE RESOLUTION: SEMANTIC FREEZE CANDIDATE / EXECUTABLE GEOMETRY PARTIAL**

**FROZEN GEOMETRY: BLOCKED**

The source is sufficiently resolved to freeze the semantic architecture of Strategy A, but not sufficiently resolved to freeze every numeric/executable coordinate required for a production detector.

The next valid gate is therefore not parameter optimization. It is a **Frozen Semantic Specification** followed by explicit unresolved-geometry research fixtures. Production implementation remains locked until executable geometry is independently resolved.
