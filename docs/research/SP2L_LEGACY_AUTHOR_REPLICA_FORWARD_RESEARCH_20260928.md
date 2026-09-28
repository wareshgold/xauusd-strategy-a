# SP2L Legacy Author Replica — 2026-09-28

Status: RESEARCH ONLY / NON-CANONICAL.

Purpose: reproduce the preserved XAUUSD author-replica family first, then run a forward test using the same research geometry and numeric configuration.

Fixed configuration:
- XAUUSD.ecn
- P-Gap price 1.0
- Spike multiplier 1.5
- Max SL distance 10.0
- TP 1R

Historical geometry:
- a=candle[i-4], spike=candle[i-3], correction=candle[i-2], trigger=candle[i-1]
- BUY entry=trigger Low; SELL entry=trigger High
- BUY SL=a Low; SELL SL=a High
- preserved P-Gap predicates and body comparisons

Previously recorded replay: 168 signals, 106W, 58L, 4 ambiguous, 163 decisive, 64.63% decisive WR, +48R, PF 1.83.

Execution boundary: the historical replay does not model a later pending fill. The legacy forward wrapper therefore uses the exact geometry/levels but retains the existing pending-order research infrastructure. Forward results must not be treated as equivalent to historical outcome semantics until fill semantics are resolved.

Frozen Geometry remains BLOCKED; this experiment does not promote any rule to canonical Strategy A.
