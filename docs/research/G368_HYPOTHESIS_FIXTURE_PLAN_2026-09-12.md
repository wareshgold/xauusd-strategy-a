# G368 — Hypothesis Fixture Plan

The next synthetic suite must use minimal pairs. Each pair changes exactly one geometric property while holding all other inputs constant.

| Pair family | Variable isolated | Expected purpose |
|---|---|---|
| PG-MP | gap endpoint/index | distinguish generic vs pressure-context interpretations |
| PG-MP-WB | wick/body overlap | expose OHLC convention dependence |
| ABCD-MP | anchor location | distinguish extreme/body/structural anchors |
| SCALE-MP | parent vs nested leg | expose scale-selection dependence |
| ENTRY-MP | trigger vs fill timing | prevent implicit fill=C assumption |
| SL-MP | origin boundary vs extreme | distinguish invalidation semantics |
| TP-MP | AB=CD vs fixed R target | distinguish geometric projection from reward convention |

Each fixture must declare expected outputs per hypothesis and retain `canonical=false`.
