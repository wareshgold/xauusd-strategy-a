# SP2L Joint Geometry: P-Gap / Entry / SL — 2026-09-08

## Scope
Research-only joint inspection of the authoritative SP2L teaching frames and the already-resolved transcript semantics. Production is unchanged.

## Source evidence used

- P-Gap teaching slide around 34:00–36:30, including the explicit `Valid BO = P-Gap` label and three accepted-looking constructions beside one rejected construction.
- Entry teaching sequence around 38:20–40:16 showing `Buy Limit`, a horizontal pending-order line, `SL`, and delete/replacement handling.
- Transcript semantics around 38:38–39:26 describing correction, pre-set Limit placement, and structural invalidation.
- Official SP2L description stating bullish correction reaches the previous candle Low, bearish correction reaches the previous candle High, and SL is behind the candle from which the Spike originated.
- Source-resolution correction that downgrades the real-chart annotations around 62:00–64:30 as reliable A/B/C/D labels.

## Joint visual finding

The P-Gap slide's shaded regions do **not** provide a common executable price anchor with the Entry/SL diagram.

The three accepted-looking P-Gap constructions place their highlighted regions at different structural locations. The rectangles overlap the illustrative candle bodies/wicks and are not drawn with numerical precision. They therefore demonstrate a **gap region associated with breakout**, not an exact OHLC boundary.

The Buy Limit diagram separately shows an order level inside the developing structure and a distinct SL below the Spike-origin structure. It does not identify the order line as the boundary of the P-Gap rectangle.

## Triangulation result

### P-Gap

**Source-supported semantic:** a distinct gap/non-overlap associated with a valid breakout/Spike.

**Still unresolved:**
- exact candle pair;
- wick vs body;
- exact boundary values;
- equality/touch behavior;
- minimum size;
- universal timing index.

### Entry

**Source-supported semantic:** pending Limit during correction; bullish correction references the relevant prior Low and bearish correction the relevant prior High.

**Strong candidate:** pending Limit at that relevant prior-candle extreme.

**Still unresolved:** whether the correction reference and actual pending-limit price are numerically identical in every Spike variant.

### SL

**Source-supported semantic:** SL behind the candle from which the Spike originated.

**Still unresolved:** exact wick/body boundary, offset/buffer, and whether origin-candle identity changes across variants.

## Important negative result

No defensible common anchor was found that lets us derive:

`P-Gap boundary -> Entry price -> SL -> Leg-1 anchor`

as one deterministic formula.

In particular, the evidence does **not** justify any of these imports:

- P-Gap = generic three-candle imbalance;
- Entry = P-Gap boundary;
- Entry = classical harmonic C;
- Entry = fixed 50% retracement;
- SL = fixed-point distance;
- SL = automatically the same candle extreme used for P-Gap;
- Leg 1 = classical A-to-B without source-specific candle mapping.

## Synthetic fixture consequences

The joint pass reduces the required discriminators to four groups:

1. **P-Gap boundary:** wick-separated/body-overlap versus body-separated/wick-overlap.
2. **Entry identity:** correction reference equals pending Limit versus correction reference differs from Limit.
3. **SL identity:** Spike-origin wick/body versus preceding structural level.
4. **Intrabar lifecycle:** touch/cross/fill versus close-back behavior.

No historical performance is permitted to select among these hypotheses.

## Gate decision

**Joint geometry resolution: PARTIAL / NO COMMON ANCHOR PROVEN.**

- SOURCE RESOLUTION: progressing
- SYNTHETIC FIXTURES: required and expanded
- FROZEN GEOMETRY: BLOCKED
- DEV: locked
- VAL: untouched
- FRESH HOLDOUT: locked
- PRODUCTION: unchanged

## Next highest-value action

The remaining source-resolution work should target the **Spike-origin candle identity across the accepted P-Gap variants** and the exact meaning of the first-low/previous-low wording. If those two items can be uniquely resolved, Entry and SL may become executable without inventing P-Gap geometry.

Until then, P-Gap, Entry price, SL price, and Leg-1 anchors must remain separate research variables.
