# SP2L V3.1 RR4 / ACT40 — Runtime Evidence Snapshot

- Snapshot date: 2026-11-03
- Evidence cutoff: 2026-11-03 06:53:35.394684 UTC / 10:23:35.394684 Asia/Tehran
- Strategy version: \`SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101\`
- Symbol: \`XAUUSD.ecn\`
- Account mode: Demo
- Magic: \`26092301\`
- Status: \`OBSERVED_LIFECYCLE_PASS / RESEARCH_ONLY / NON_CANONICAL\`

## Scope and conclusion

This snapshot records the V3.1 runtime evidence supplied for one completed trade and the associated Event Ledger. The observed order-to-position-to-exit lifecycle is internally consistent. The order placement was accepted and verified, the position was observed, two trailing-stop modifications were accepted by MT5, the updated SL values appeared in subsequent position lifecycle events, and the position was subsequently closed by SL with a positive net result.

**No defect was identified in this reviewed trade lifecycle.** This is a bounded observation, not proof that the whole version is bug-free. One completed trade cannot establish statistical edge, reliability across market conditions, or absence of latent defects.

No canonical Strategy A geometry or execution semantics are approved by this snapshot. The event records explicitly report \`canonical=false\`, \`demo_only=true\`, and \`PENDING_LIMIT_RESEARCH\`.

## Runtime configuration recorded for this version

| Setting | Observed/configured value |
|---|---:|
| P-Gap | 1.0 |
| Spike multiplier | 1.5 |
| Maximum SL distance | 10 |
| TP_R | 4 |
| Trailing pips | 4 |
| Trailing distance | 0.40 price |
| Symbol point / tick size | 0.01 |
| Volume | 0.01 |
| Order mode | PENDING_LIMIT_RESEARCH |
| SL anchor | SPIKE_CANDLE_EXTREME_RESEARCH |
| Canonical | false |

The candidate event reports \`pip_size=0.01\` and \`pip_method=POINT_FOR_NON_FX_DIGITS\`. This is an observed event field, not a new canonical pip definition.

## Completed trade evidence

Signal: \`XAUUSD.ecn:1793695800:SELL\`

| Lifecycle item | Evidence |
|---|---|
| Candidate | SELL; theoretical entry 3916.54; SL 3925.66; TP 3880.06 |
| Order result | \`ok=true\`; retcode 10009; order 65001173; active-order verification passed |
| Position opened | Position 65001173; actual entry 3916.60; volume 0.01 |
| Initial position SL / TP | 3925.66 / 3880.06 |
| First trailing attempt | Deferred at 06:52:01.374739 UTC; reason \`CURRENT_QUOTE_OR_BROKER_DISTANCE\` |
| First successful trailing update | 06:52:07.873275 UTC; SL 3925.66 → 3915.59; retcode 10009 |
| Position confirmation | 06:52:09.888535 UTC; position event reports SL 3915.59 |
| Second successful trailing update | 06:53:02.493521 UTC; SL 3915.59 → 3914.65; retcode 10009 |
| Position confirmation | 06:53:04.506432 UTC; position event reports SL 3914.65 |
| Exit | 06:53:35.394684 UTC; \`DEAL_REASON_SL\`; exit price 3914.67 |
| Gross P/L | +1.93 |
| Commission | -0.05 |
| Swap | 0.00 |
| Net P/L | **+1.88** |
| Telegram deal notification | HTTP_200 |

The deferred attempt was followed approximately 6.5 seconds later by a successful update for the same position and completed bar. It is therefore classified as a deferred/retried operation, not a terminal failure.

The final exit price was 0.02 above the final SL for this SELL trade. This is consistent with a small adverse execution difference; it is not evidence of an SL modification failure.

Independent price-based calculation using actual entry and initial SL:

- Initial price risk: 3925.66 − 3916.60 = 9.06
- Favorable exit movement: 3916.60 − 3914.67 = 1.93
- Price-based result: approximately +0.213R

This R value is independently calculated for this trade; it is not an engine-provided field.

## Runtime process and monitor boundary

At the user-reported Monitor restart verification:

- Monitor PID: 4672
- Dashboard: \`http://127.0.0.1:8791\`
- API: \`http://127.0.0.1:8791/api/status\`
- Resolved data root: \`D:\\Mirzaei\\Private\\1\\xauusd-strategy-a-v3-1-trailing-retry-20261103\`
- Runner PIDs before and after Monitor restart: \`11352,9088\` — unchanged
- Event count reported by Monitor: 16

The Monitor is filesystem-only. It does not initialize, query, or shut down the MT5 terminal. Its state position IDs are tracked identifiers and are not broker-confirmed live position inventory.

## Runner source fingerprints supplied for this snapshot

| File | SHA-256 |
|---|---|
| \`scripts/run_sp2l_v3_1_xauusd_forward_test.py\` | \`1E50F4AC41A397BB0FFA7DA7A2A2678E7066FCB1634DFD7190DA4D219812DE49\` |
| \`scripts/run_sp2l_author_replica_multi_symbol_forward_test.py\` | \`889155AC4E4DF6E4CE8B21B566415747DC017E9FB3919544D701A1EF80C40EE3\` |
| \`scripts/sp2l_trailing_rules.py\` | \`9233BBBC1111DFF864795A6B29F561E34B36EAADB4D760AF895A320445D3CB72\` |
| \`scripts/sp2l_trailing_state.py\` | \`05AB1430105D1DF928BA1EC11FCB8F7312464982925AF2CFC72E48FCEEE7E2E6\` |

These are user-supplied local file fingerprints. This snapshot does not independently re-hash the user's local worktree.

## Explicit limitations

1. Evidence covers one completed Demo trade and the event records provided for it.
2. No direct MT5 broker query was performed by the Monitor; no claim is made about current live positions after the recorded exit.
3. No statistical edge, robustness, or out-of-sample validation is claimed.
4. No source-resolution or canonical-geometry decision is made.
5. No Runner code, order behavior, MT5 connection, or live process was changed or restarted to create this snapshot.

## Snapshot disposition

**Observed result:** the supplied V3.1 trade lifecycle completed coherently, including successful trailing updates and a positive net SL exit. No defect is confirmed in this evidence slice.

**Operational priority:** improve the read-only Dashboard so that failed order/trailing operations, unresolved deferred updates, session/connection errors, and their actionable context are surfaced directly, with all displayed event times in Tehran time.

