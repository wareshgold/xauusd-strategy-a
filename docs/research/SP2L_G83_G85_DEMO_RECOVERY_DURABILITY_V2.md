# G83-G85 Demo Recovery Durability

G83 adds an append-only sequence journal. G84 rejects event gaps and reordering. G85 reconstructs known order lifecycle state after restart without interpreting unknown events as success.

This is research/demo infrastructure only. Strategy geometry, BUY/SELL generation, real broker connectivity, and production authorization remain outside this gate.