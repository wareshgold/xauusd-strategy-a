# SP2L Research Snapshot — Trailing Transition Audit — 2026-09-30

## Scope
NON_CANONICAL_FORENSIC only. This audit compares the exact 1,508-signal V2 population under the RR=1 trailing OFF baseline versus trailing 10/20/30/50 pip variants.

## Integrity
- Population signals: 1,508 for every variant
- Identity mismatches: 0 for every variant
- Baseline: 68.039867% WR, +543.0R, $1,590.25
- Trailing 10p: +171.3383065R / +$817.14 versus OFF
- Trailing 20p: +90.9421173R / +$501.95 versus OFF
- Trailing 30p: +45.9724985R / +$276.37 versus OFF
- Trailing 50p: +9.4470663R / +$75.76 versus OFF

## Transition accounting
10p:
- LOSS_TO_WIN 462
- LOSS_TO_LOSS 17
- WIN_TO_WIN 967
- WIN_TO_AMBIGUOUS 57
- LOSS_TO_BREAKEVEN 2
- AMBIGUOUS_TO_WIN 2
- AMBIGUOUS_TO_AMBIGUOUS 1

20p:
- LOSS_TO_WIN 319
- LOSS_TO_LOSS 161
- WIN_TO_WIN 991
- WIN_TO_AMBIGUOUS 31
- WIN_TO_BREAKEVEN 2
- LOSS_TO_BREAKEVEN 1
- AMBIGUOUS_TO_AMBIGUOUS 3

30p:
- LOSS_TO_WIN 173
- LOSS_TO_LOSS 308
- WIN_TO_WIN 1015
- WIN_TO_AMBIGUOUS 8
- WIN_TO_BREAKEVEN 1
- AMBIGUOUS_TO_AMBIGUOUS 3

50p:
- LOSS_TO_WIN 39
- LOSS_TO_LOSS 442
- WIN_TO_WIN 1024
- AMBIGUOUS_TO_AMBIGUOUS 3

## Interpretation boundary
The transition audit demonstrates that the USD/R differences arise from exit-path changes on the same signal population. It does not establish that any trailing value is source-confirmed, canonical, or robust out-of-sample. No trailing variant is selected or promoted from this artifact.

## Next research stage
Proceed to robustness/stability testing on a time-separated sample. Preserve the RR=1 Forward reference and treat trailing as a noncanonical experimental layer until source resolution is complete.
