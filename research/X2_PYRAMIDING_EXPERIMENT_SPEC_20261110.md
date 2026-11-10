# SP2L X2 Pyramiding Experiment — Offline Specification

Date: 2026-11-10
Status: IMPLEMENTED DRAFT — synthetic suite expanded; latest local execution pending; full replay not run
Research-only; non-canonical; no production or forward-runner changes.

## Objective

Test whether adding one same-direction X2 entry after X1 has moved favorably improves portfolio gross return and risk-adjusted performance, without averaging down and without increasing the initial per-signal risk budget.

This is an independent experiment. It must not alter the frozen 603-variant management matrix or its evidence.

## Immutable inputs

Use exactly the frozen inputs already used by the 603-variant matrix:

- M1 CSV SHA256: B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285; 29,919 M1 bars; 21 timestamp gaps.
- Entry CSV SHA256: 39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1; 462 entries.
- Symbol metadata: XAUUSD.ecn; point 0.01 (metadata only); contract size 100; X1 volume 0.01.
- No signal rebuild, no entry changes, no MT5, no runner/dashboard access.

## X1 control management

Run each X1 parent under both leading fixed-distance trailing controls:

1. FDT_A0.5_D0.3: activation 0.5 XAU price units; trailing distance 0.3 XAU price units.
2. FDT_A0.75_D0.3: activation 0.75 XAU price units; trailing distance 0.3 XAU price units.

These controls are included because they are the leading balanced and gross-profit candidates from the 603-variant discovery run. They remain research candidates, not selected production settings.

For each parent control, also produce an X1-only baseline with identical execution/replay assumptions.

## X2 trigger: one deterministic continuation entry

Run three threshold variants only: X2-A after +1.0R, X2-B after +1.5R, X2-C after +2.0R favorable excursion from X1 entry.

For BUY (SELL is exactly symmetric):

1. Threshold is first reached by a completed post-entry M1 bar. The threshold-reaching bar only arms the setup; it cannot also count as the pullback bar.
2. After arming, track the best favorable extreme (highest high for BUY, lowest low for SELL).
3. A pullback is confirmed only after a later completed bar has retraced at least 0.25 × X1 initial risk from that best favorable extreme. Track the pullback extreme (lowest low for BUY, highest high for SELL) from the first qualifying pullback bar onward.
4. After pullback is armed, continuation confirmation occurs when a completed bar closes above the immediately preceding completed bar's high (BUY), or below its low (SELL).
5. X2 theoretical fill is the next M1 bar's open. No same-bar close fill, intrabar sequencing assumption, or look-ahead is allowed.
6. If the next bar is unavailable, a data gap intervenes, the opening price is already through the proposed X2 stop, or X1 has exited before continuation confirmation, X2 is not opened. An X1 exit on a threshold or pullback bar cancels the setup because no X2 confirmation occurred. If X1 stop/exit and X2 continuation confirmation are both possible in the same M1 bar, mark the X2 opportunity ambiguous and do not open it.
7. X2 initial stop is the pullback extreme: below X2 entry for BUY, above X2 entry for SELL. Reject invalid/non-positive stop distance. No guessed structural anchor or additional buffer is introduced.

## Risk budget and volume

- X1 volume remains 0.01.
- Initial per-signal risk budget is X1 initial price risk × 0.01 × contract size.
- At the proposed X2 entry, compute X1's remaining open risk from its then-active stop. If X1 stop is already at or beyond breakeven in the favorable direction, its remaining open risk is zero; otherwise use the positive distance from X1 entry to its active stop × X1 volume × contract size.
- Residual X2 risk budget = max(0, initial per-signal risk budget − X1 remaining open risk).
- X2 volume remains fixed at 0.01. Open X2 only if its stop-distance risk × 0.01 × contract size is no greater than the residual budget (within a documented floating-point tolerance). Otherwise record X2_SKIPPED_RISK_BUDGET.
- Do not increase volume, round to broker lot steps, or model partial sizing. Broker minimum/step constraints are not available in this frozen OHLC dataset and must be reported as not modeled.
- This cap is an open-risk cap at X2 admission; report both X1 and X2 risk at admission and the maximum observed combined open risk.

## X2 trade management

- X2 uses the same fixed-distance trailing rule as its parent X1 control: activation 0.5 or 0.75 XAU price units and distance 0.3 XAU price units, measured from X2's own entry and using X2's own initial stop/risk.
- X1 and X2 are independent legs with independent stops. Do not merge their entry prices or average the positions.
- Both legs use completed-bar updates that become active on the next M1 bar.
- X1 retains the existing matrix convention: its frozen entry bar is excluded. X2 is filled at the next M1 bar open, so its entry bar's subsequent high/low must be checked against its initial stop; do not exclude that bar. No trailing-stop update is calculated from the X2 entry bar.
- A gap while either leg is open is ambiguous; do not infer fills.
- Same-bar stop/target conflicts are ambiguous. There is no final TP in this X2 experiment.
- If X1 and X2 are both open, process their stop checks on each bar before any new stop updates; any newly calculated stop is active on the next bar.
- X1 exit before X2 admission cancels the X2 setup. An exit and X2 trigger on the same bar is ambiguous and cancels X2.

## Required comparisons and metrics

Produce 8 configurations:

- X1-only controls: FDT_A0.5_D0.3 and FDT_A0.75_D0.3.
- X2 overlays: each of the two parent controls × thresholds +1R, +1.5R, +2R.

For each configuration report:

- X1 count, X2 opportunities, X2 opened, skipped by risk budget, ambiguous/cancelled opportunities.
- Decisive, ambiguous, gap-exposed and open/unresolved counts by leg and by combined signal.
- Combined gross USD and R, profit factor, max drawdown by exit-time cohorts, average R, win/loss/BE counts.
- X1-only versus X1+X2 paired delta for every original population key.
- X2 incremental gross USD, X1 remaining open risk and X2 risk at each admission attempt, maximum combined open risk, and distribution of X2 holding time.
- Profit concentration excluding top 1/3/5/10 combined winners.
- No ranking may hide unresolved/ambiguous counts. Discovery ranking is secondary to risk and completeness.

## Conservative data semantics

- Use the same 462-entry frozen population and exact M1 bars.
- Never fill or interpolate M1 gaps.
- Use only completed bars for arming, pullback and confirmation.
- Fill X2 only at the next bar open.
- If a bar can contain conflicting events whose order cannot be established from OHLC, mark ambiguous or skip the X2 admission; never assume the favorable sequence.
- Aggregate same-minute realized PnL before drawdown calculations; do not invent intraminute ordering.
- Costs (spread, commission, slippage) remain NOT_MODELED and all PnL is gross, not broker net profit.

## Required tests before any full replay

Synthetic tests must cover:

- BUY and SELL symmetry.
- Each +1R/+1.5R/+2R arming threshold.
- Threshold bar cannot double as pullback bar.
- Pullback depth exactly 0.25R and just below 0.25R.
- Confirmation uses prior completed bar high/low and fills next bar open.
- No X2 if X1 exits before confirmation, including on threshold/pullback bars.
- Same-bar X1 exit and continuation-confirmation ambiguity; combined signal must remain unresolved.
- Invalid/gap-crossed next-bar entry and invalid stop side.
- Risk-budget admission, exact cap boundary, and risk-budget rejection.
- X2 initial stop remains immutable in output while its final stop trails; X2 management remains independent after X1 exits.
- Next-open-through-stop rejection and combined ambiguity propagation.
- X1 and X2 independent stop management and next-bar activation.
- Gap ambiguity, X1 entry-bar exclusion, X2 next-open entry-bar stop handling, and same-minute drawdown cohort invariance.
- No MT5 import/API or live-runner references in the implementation.

## Safety and evidence

- New isolated branch only: research/x2-pyramiding-offline-20261110.
- Never modify or overwrite the 603-matrix artifacts.
- Output must be a new exclusive-create timestamped directory with trades CSV, summary CSV, manifest and SHA256SUMS.
- Manifest must record both frozen input hashes, exact rule semantics, all eight configurations, risk cap, costs not modeled, and research_only=true / canonical=false / mt5_accessed=false.
- No merge, no canonical promotion, no Fresh Holdout claim, and no live-runner change.
- Actual full replay is permitted only after implementation and all synthetic tests pass.