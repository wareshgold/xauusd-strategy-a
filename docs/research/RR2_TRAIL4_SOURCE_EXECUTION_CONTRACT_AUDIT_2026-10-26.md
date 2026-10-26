# RR2/TRAIL4 Source Contract Audit — 2026-10-26

Status: **PARTIALLY SOURCE-VERIFIED / REPLAY BLOCKED**  
Authority: research profile only; this is not canonical SP2L Strategy A geometry.

## Exact source identity

- Repository: `wareshgold/xauusd-strategy-a`
- Runner: `scripts/run_sp2l_v3_xauusd_forward_test.py`
- Runner ref: `fix/rr2-trail4-telegram-deal-time-20261013`
- Runner Git blob SHA: `b0702856292e265c57d63134b414a618567a2842`
- Config: `scripts/sp2l_v3_rr2_trail4_config.py`
- Config Git blob SHA: `5f5c123587bd81028d353560afb8d2763fa33f98`
- Profile: `SP2L_V3_XAUUSD_RR2_TRAIL4_20261001`

Source links:
- [Runner](https://github.com/wareshgold/xauusd-strategy-a/blob/fix/rr2-trail4-telegram-deal-time-20261013/scripts/run_sp2l_v3_xauusd_forward_test.py)
- [Research config](https://github.com/wareshgold/xauusd-strategy-a/blob/fix/rr2-trail4-telegram-deal-time-20261013/scripts/sp2l_v3_rr2_trail4_config.py)

## Source-confirmed research-profile behavior

The following describe this specific code revision only:

| Area | Source-observed behavior | Replay status |
|---|---|---|
| Signal bars | Detector receives three OHLC candles named before, spike, after. | Reproducible from OHLC if candle construction/timeframe are pinned. |
| P-Gap candidate condition | BUY uses `after.low > before.high + 1.0`; SELL uses `after.high < before.low - 1.0`. | Research-profile formula only; not canonical P-Gap meaning. |
| Spike-body condition | Spike body must be strictly greater than 1.5 times both neighboring candle bodies. | Reproducible from OHLC. |
| Entry trigger | For BUY, first later candle whose low is below previous candle low; theoretical entry is that current candle low. SELL mirrors using highs. | Theoretical trigger reproducible from OHLC; executable fill is not established by this function. |
| Initial stop | Uses the candle at `candles[start_index - 2]` low for BUY / high for SELL. | Code behavior known; source/canonical SP2L anchor unresolved. |
| Risk filter | Rejects risk <= 0 or > 10.0 price units. | Reproducible as profile behavior. |
| Initial target | TP = theoretical entry +/- 2R. | Profile behavior; actual broker execution and realized PnL still require deal evidence. |
| Secondary 2X | Candidate stores secondary entry at 0.5R adverse to theoretical entry. | Candidate value known; order placement/sizing/management must be verified separately. |
| Pending mode / TTL | Config selects `PENDING_LIMIT_RESEARCH`, TTL 30 minutes. Expiry code scopes XAUUSD + configured magic + Buy/Sell Limit and fails closed if server clock freshness cannot be verified. | TTL policy is code-confirmed; exact order placement price and all rejection/retry outcomes need adapter contract coverage. |
| Trailing | After lifecycle monitoring, runner reads one M1 bar at shift 1 (completed bar); BUY target is bar high minus 0.4; SELL target is bar low plus 0.4. | Target calculation known. Broker stops/freeze distance, current Bid/Ask checks, modification acceptance, and missed/deferred updates must be represented explicitly. |
| Fill/exit evidence | Forward runner logs observed broker order/deal/position facts, including profit, commission, swap and net. | Historical simulator must not fabricate these as if observed. |

## Mandatory replay blockers

A replay adapter must remain **BLOCKED** until each item below has an explicit, versioned resolution:

1. **Executable entry semantics:** the detector returns a theoretical price, but the actual generic runner's order-send path and price normalization must be traced end-to-end for this exact revision.
2. **Intrabar sequencing:** OHLC alone cannot establish the order of entry, SL, TP, and trailing events inside a candle. Tick replay must preserve source row order; same-millisecond rows with differing quotes remain order-sensitive unless a source-backed tie-break rule exists.
3. **Fill model:** pending limit touch/cross, slippage, partial fill, rejection, and quote-side conventions cannot be inferred from the candidate function.
4. **Costs:** commission, swap, spread treatment and any slippage model must be pinned to an explicit, reproducible contract before net metrics are accepted.
5. **Trailing modification:** a desired stop level is not the same as an accepted broker modification. Stops/freeze checks and deferred/rejected modifications need deterministic modeled states, with any unmodeled case marked unresolved.
6. **2X order lifecycle:** a calculated secondary entry does not prove that the runner submits, sizes, expires, or manages that order.
7. **Candle construction:** the exact MT5 M1 bar boundaries, missing-bar policy, and time basis must be frozen and tied to the dataset manifest.
8. **Dataset binding:** the local tick file is not present in this repository. Replay must bind the exact external file SHA-256 and audit manifest; it must never silently substitute a different dataset.

## Gate decision

- OHLC-only research may test the source-coded candidate geometry as a clearly labeled **profile replication**, not canonical SP2L and not tick-feasible execution.
- Tick Bid/Ask data is necessary for an execution-aware replay, but data availability alone does not establish fill semantics.
- No historical performance claim or Strategy A/B winner can be produced from this contract audit.
- Do not implement a permissive fallback for any blocker. Return `BLOCKED`, `AMBIGUOUS`, or `UNRESOLVED` with a reason.
- Keep the 2026-09-07 session-gap treatment provisional until the broker-specific schedule is independently confirmed.
- Do not merge or promote this research profile to production on the basis of code matching alone.

## Next acceptance gate

Before building the replay engine, add fixture cases from the exact order-send and lifecycle code paths and have the source contract reviewed. Then implement a deterministic event reducer whose output distinguishes observed facts, modeled outcomes, and unresolved outcomes. Any modeled fill/cost rule must be explicitly authorized and fingerprinted; no optimizer may tune unresolved execution semantics.
