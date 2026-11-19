# V3.1 Historical Replay Contract — 2026-11-19

Status: research specification; no performance replay has been run yet.

## Source facts verified from the V3.1 runner/gateway

- Entry orders use `PENDING_LIMIT_RESEARCH`.
- BUY pending orders are placeable only when theoretical entry < current Ask; SELL pending orders only when theoretical entry > current Bid.
- Submitted pending order levels are theoretical entry, theoretical SL and theoretical TP.
- Pending order request uses GTC at the broker, while the runner cancels its own unfilled pending orders after 30 minutes by default.
- The gateway's `MAX_OPEN_POSITIONS` defaults to 1. Its exposure count includes both the gateway's own open position(s) and pending order(s). A new signal is rejected with `MAX_OPEN_POSITIONS` when this slot is occupied.
- Trailing excursion is based on completed M1 candle high/low. Activation is a favorable price move of 0.40 from entry; trailing distance is 0.40. The trailing SL is normalized to tick size and must remain on the valid side of the executable quote plus the broker minimum stop distance.
- BUY position exits are evaluated against Bid; SELL position exits against Ask.

## Consequences for the 89-run matrix

1. The 40 Dual configurations describe two independent simultaneous legs. They cannot be represented as two separate pending orders/positions under the current V3.1 gateway's default one-exposure limit. They must be reported as **NOT EXECUTABLE UNDER CURRENT RUNNER GUARD** unless a separately specified one-order partial-close implementation is researched and tested. Do not silently simulate two simultaneous broker exposures as if the current runner could submit them.
2. The exact fixed-0.01 Runner reference and eight normalized Runner configurations are single-exposure candidates.
3. The 40 Fixed-TP configurations are single-exposure candidates.
4. The first executable portfolio replay scope is therefore 49 configurations (40 Fixed TP + 9 Runner) under the one-exposure rule. The 40 Dual variants remain in the matrix manifest but are blocked from runner-compatible portfolio ranking.
5. Candidate entry timestamps identify the M1 trigger candle, not a recorded broker order-submission timestamp. Historical order submission time is unavailable. Replay must therefore expose a declared latency assumption (baseline plus sensitivity) after the trigger candle completes; it must not claim exact historical submission timing.
6. Spread is represented by using executable quote sides (Ask for BUY entry, Bid for SELL entry; Bid for BUY exit, Ask for SELL exit). Commission, swap, historical stop-level metadata and slippage schedules are not present in the current evidence bundle. Results must be labelled gross of those missing costs; do not invent them.
7. A following tick after a candidate timestamp does not prove a pending-order fill. Fill eligibility must be tested against the correct executable side and placeability condition. A pending order that does not fill within 30 minutes expires.
8. The frozen entry CSV is the common population. No signal search or entry discovery may cross an M1 gap. Tick gaps and missing intrabar paths must be retained in per-trade ambiguity metadata; never fabricate ticks or prices.
9. No ranking, Fresh Holdout unlock, canonical decision, live runner change, or merge is authorized by this specification.

## Required replay outputs

- One row per candidate/run with statuses including FILLED_AND_CLOSED, UNFILLED_EXPIRED, REJECTED_NOT_PLACEABLE, REJECTED_EXPOSURE_BUSY, INFEASIBLE_SIZE, and AMBIGUOUS_DATA.
- Entry submission assumption, fill timestamp/quote/price, theoretical entry, fill deviation, initial SL/TP, trailing updates, exit quote/price/reason, gross P&L, R multiple, lot size, requested and actual risk, and ambiguity flags.
- Run-level summary must distinguish executable trade count, unfilled/rejected candidates, ambiguous trades, gross results, and unavailable cost components.
- SHA-256 manifest for all inputs, code/config, and outputs.

## Safety boundary

Offline Python only. No MetaTrader5 import, terminal access, network dependency, order API, or runner/dashboard mutation.
