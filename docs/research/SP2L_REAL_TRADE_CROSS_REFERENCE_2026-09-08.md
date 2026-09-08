# SP2L Real-Trade Cross-Reference Audit — 2026-09-08

## Objective
Cross-reference the four XAUUSD trades shown in the authoritative source recording against the source-confirmed SP2L semantics for P-Gap, Entry, and structural SL.

This is a source-evidence audit only. No backtest result is used to select an interpretation.

## Source material inspected
- Uploaded authoritative SP2L recording.
- Source-visible XAUUSD chart frames around the four-trade example.
- Order-history frames around 59–62 minutes of the recording.
- Existing source transcript evidence for correction, pending-limit entry, P-Gap, and structural SL.

## Four visible trades

| Trade | Direction | Entry | SL | TP field | Entry→SL distance |
|---|---|---:|---:|---:|---:|
| T1 | SELL | 3229.08 | 3237.73 | 0.00 | 8.65 |
| T2 | SELL | 3223.84 | 3235.50 | 3213.37 | 11.66 |
| T3 | SELL | 3228.88 | 3235.50 | 3213.37 | 6.62 |
| T4 | SELL | 3232.41 | 3237.80 | 0.00 | 5.39 |

`TP field = 0.00` is preserved as the source-visible order-table value; it is not interpreted as a target price.

## Entry cross-reference

The real-trade chart frames show several manually drawn horizontal levels in the corrective structure. The short-side annotations are consistent with the source narration that a bearish correction reaches the high of the relevant previous candle and that a SELL LIMIT can be prepared there.

The strongest source-safe conclusion is therefore:

`bearish SPIKE -> correction -> previous/relevant HIGH context -> pending SELL LIMIT`

The four trades do **not** establish a universal executable candle index. The screenshots cannot prove, for every fill, whether the level is the wick extreme, body edge, a particular prior candle, or a revised level after additional correction candles.

The four trades also show multiple distinct entry prices. This is consistent with the source explanation that an order may be deleted/replaced when the evolving correction changes the resulting stop distance. It is not evidence for a fixed numerical entry formula.

## P-Gap cross-reference

The real-trade frames show the Spike/correction/trading sequence clearly enough to preserve the setup context, but they do not expose a machine-readable P-Gap rectangle with a uniquely identifiable pair of OHLC fields. The annotated horizontal trade levels are execution/management levels, not sufficient evidence for the P-Gap boundary.

Therefore the four trades do **not** resolve:
- exact P-Gap candle identity;
- exact P-Gap OHLC fields;
- wick vs body boundary;
- minimum gap size;
- equality/touch convention.

This is important: a visible trade can validate that a P-Gap-qualified Spike context was used without allowing us to reverse-engineer the P-Gap formula from the order table.

## SL cross-reference

All four stops are structurally above the corresponding short entry context, with materially different entry-to-stop distances. This supports the source semantic that the stop is placed behind the Spike-origin structure rather than at a fixed number of points.

However, the observations do not uniquely identify:
- exact origin candle for every variant;
- wick vs body boundary;
- strict beyond vs touch;
- fixed buffer.

The distances 8.65, 11.66, 6.62, and 5.39 must remain descriptive observations only.

## Cross-component result

| Component | Source-safe result | Executable geometry |
|---|---|---|
| P-Gap | valid Spike/breakout context includes P-Gap/non-overlap evidence | unresolved |
| Entry | bearish correction reaches previous/relevant High context; pending SELL LIMIT semantics | unresolved exact candle/price |
| SL | behind Spike-origin structure | unresolved exact boundary/buffer |
| Leg 1 / AB=CD | equal/approximately equal second-leg semantic | unresolved exact anchors/tolerance |

## Important negative result
The four trades do **not** provide enough evidence to unlock Frozen Geometry. In particular, the order history cannot be used to infer the P-Gap formula or a universal Entry formula simply by finding a profitable numerical fit.

The secondary TradingFinder material remains non-canonical where it introduces additional executable details such as last-Spike-candle breakout/reclaim.

## Gate decision
**SOURCE RESOLUTION:** semantic cross-component relationship strengthened.

**FROZEN GEOMETRY:** still BLOCKED.

**DEV:** LOCKED.

**VALIDATION:** LOCKED and untouched.

**FRESH HOLDOUT:** LOCKED and untouched.

**PRODUCTION:** unchanged.

## Next highest-value source action
The remaining highest-value source question is not another optimization/backtest. It is a tighter visual mapping of one or more real examples where the exact corrective candle and the exact pending order line are simultaneously visible, followed by a search for the same relationship in another example. If the source still does not uniquely identify wick/body/index behavior, preserve the unresolved state and move to source-documentation completeness rather than guessing.
