# G36 Geometry Decision Table

| Blocker | Source-confirmed meaning | Candidate state | Production status |
|---|---|---|---|
| B1 P-Gap | Valid BO associated with P-Gap; distinct from generic gap/FVG shortcut | Exact OHLC geometry unresolved | BLOCKED |
| B2 Entry | Pending Limit during correction at relevant structural level | Universal anchor unresolved | BLOCKED |
| B3 SL | Structural invalidation separate from Entry | Exact OHLC anchor unresolved | BLOCKED |
| B4 Trigger | One/two/three-candle and key-bar trigger family | Acceptance/timing unresolved | BLOCKED |
| B5 AB=CD | Leg2 magnitude linked to Leg1 magnitude | A/B/C/D anchors and tolerance unresolved | BLOCKED |
| B6 Leg2/TP | Second-leg continuation; TP1 preferred; TP2 larger/research candidate | Executable projection unresolved | BLOCKED |

## Result

No blocker is promoted to canonical executable geometry in G36.

The semantic layer is frozen enough to support research infrastructure, but the executable Strategy A detector remains prohibited until source-unique geometry is established.
