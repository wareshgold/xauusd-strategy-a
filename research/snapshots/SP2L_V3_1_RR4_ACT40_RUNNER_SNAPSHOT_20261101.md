# Strategy A V3.1 – RR4 / ACT40 / TRAIL40

Created UTC: 2026-11-02T04:54:23Z

Status: RESEARCH / FORWARD CANDIDATE ONLY.
Runner execution: NOT STARTED.
MT5 orders: NONE submitted by this preparation.

## Git provenance

Repository: wareshgold/xauusd-strategy-a
Branch: research/strategy-a-v3-1-rr4-act40-20261101
Base HEAD: dac76b09da01f022d745f51328ee703f6fb59851

The source V3 runner has local modifications relative to Base HEAD.
Those modifications are intentionally preserved and included in the V3.1 source copy.
They have NOT been committed as part of this V3.1 preparation.

## Source and artifact hashes

Source runner: `scripts\run_sp2l_v3_xauusd_forward_test.py`
SHA256: 0FE5B67D33BC93D9A7244C79B951F91E9A00A616960C2AD6DFD4E292611DC873

Source config: `scripts\sp2l_v3_rr2_trail4_config.py`
SHA256: F70B0DCC4C50E6D95FFAC2E39AFB1CA044830027FEACFC1D1E21ECDAD40E24E8

V3.1 runner: `scripts\run_sp2l_v3_1_xauusd_forward_test.py`
SHA256: 4DFEF376E2B16252351B71374B4D03E99D4F9CE4EC761195C9E6F139D011452C

V3.1 config: `scripts\sp2l_v3_1_rr4_act40_config.py`
SHA256: 201C013157DDAC51054982BD0171B7AC5E1BA4E1F06792100A8452889A2F5DEC

Shared multi-symbol runner (unchanged by this task):
SHA256: 238AE453292BA4CDFEA64E463A0BC93D76040721CD8709DF5FBA84DA725EBDD5

## Exact change boundary

V3.1 runner is byte-for-byte derived from the current local V3 runner,
with only these substitutions:
- Config import points to V3.1 config.
- Events JSONL path is isolated for V3.1.
- Runtime State path is isolated for V3.1.

V3.1 config is byte-for-byte derived from V3 config,
with only:
- VERSION changed to SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101
- TP_R changed from 2.0 to 4.0

Normalized source comparisons: PASS.
Python AST syntax validation: PASS.

## Exit management

TP_R: 4.0
Trail activation: 0.40 price units
Trail distance: 0.40 price units
TRAIL_PIPS: 4.0
XAU_PIP_SIZE_PRICE: 0.1

No new trailing algorithm was introduced.

## Entry and execution logic

Entry logic is inherited unchanged from the local V3 runner.
P-Gap, spike, initial SL, pending lifecycle, TTL, history handling,
and other execution behavior are not intentionally redesigned here.

## Research evidence

Frozen population: 462 entries.
Frozen entries SHA256:
39ED87CD1F0BE3E59B5F064B0BCF97A9787E5266DF6E972AA07E5EA4D3608AB1

M1 dataset: 29,919 bars.
M1 SHA256:
B0782E716C7ECCBD29EF25E146C088B356F2AADF2CCD5D7EA24E6AC1488AA285

Exploratory RR4/ACT40 result:
Net +208.601156R; PF 8.1931; trade-exit-ordered max DD 2.4977R.

These are in-sample M1 OHLC research results, not production validation.
Tick sequencing, spread, commission, slippage, broker rejections, and
Fresh Holdout validation remain outstanding.

## Isolation and safety

V3 source files are not modified by this snapshot operation.
Existing staged, unstaged, and untracked user evidence must be preserved.
Only the two V3.1 files and this snapshot may be considered for the V3.1 commit.
No broad staging is permitted.

Forward start requires separate review and explicit user authorization.

## Safety isolation amendment — 2026-11-02

Follow-up branch: `research/strategy-a-v3-1-magic-clock-guard-20261102`

- V3.1 sets `SP2L_MAGIC_BASE=26092300` before importing the shared runner.
- XAUUSD V3.1 magic is therefore `26092301`; original V3 remains `26092201`.
- The historical hard-coded/default UTC+03:00 offset has been removed.
- Pending expiry continues to fail closed if `SP2L_PENDING_SERVER_OFFSET_HOURS` is absent or invalid.
- An additional execution guard blocks every order attempt unless the operator explicitly pins the offset and both the broker tick freshness check (120-second tolerance) and MT5 strict offset helper agree.
- The guard does not infer or silently set the server offset.
- No V3 source file, V3 state file, or V3 events file is modified.
- No runner was started and no MT5 order was submitted by this amendment.

The prior exploratory M1 results remain in-sample and are not a production validation. The V3.1 branch remains research/forward-test only.


## Post-entry trailing safety correction — 2026-11-02

A code review found that the V3.1 trailing loop used the latest completed M1
bar without checking whether that bar began after the individual position
opened. This could incorrectly count pre-entry High/Low movement toward
trailing activation.

Correction on this branch:
- Added `completed_bar_is_after_position()` to the V3.1 config module.
- The guard prefers MT5 `position.time_msc`; it falls back to `position.time`
  only when the millisecond timestamp is unavailable.
- A completed bar is eligible only when its start timestamp is strictly later
  than the position entry timestamp. The entry minute itself is conservatively
  excluded, even when the position opens at the first second of that minute.
- Missing/invalid timestamps fail closed: no trailing update is attempted.
- Added `scripts/test_sp2l_v3_1_trailing_bar_guard.py` with regression cases
  for pre-entry, same-minute, post-entry, fallback, and missing timestamps.
- Added a hard Demo-only execution gate: if MT5 account information is missing
  or account trade mode is not `ACCOUNT_TRADE_MODE_DEMO`, new order execution
  is blocked. A future live-money deployment requires a separate reviewed code
  change; this branch cannot be used on a live account.

Validation performed in this chat:
- 7 synthetic timestamp assertions: PASS.
- The actual Windows MT5 runner has NOT been executed after this correction.
- No live or demo orders have been submitted by this correction.
- Local Windows worktree synchronization, MT5 runtime smoke test, and demo
  account verification remain required before the runner can be started.

Commits:
- Config helper: `1ed6c547a98a14c959751e051099e58bb79e5050`
- Runner guard + Demo-only gate: `1a66c6c21b0d36cb374ca7ac0bf88a5ed5ff3c3a`
- Regression tests: `725afb75e4c79c3d09e2fe396268506d771f4ae6`
