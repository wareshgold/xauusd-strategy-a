# Unified Offline Management Matrix — 2026-11-09

Research-only batch: 603 variants × 462 frozen entries = 278,586 replays. No MT5 initialization, signal rebuild, live-runner changes, or overwrite of prior evidence.

## Families
Fixed RR 1/1.5/2/3R (4); no target (1); BE activation 0.5/1/1.5R (3); fixed-distance trailing without TP: 10 activation price levels (0/0.25/0.5/0.75/1/1.5/2/3/4/6) × 11 distance price levels (0.2/0.3/0.4/0.5/0.7/1/1.5/2/3/4/6) (110); Step-Lock no TP (1); Step-Lock plus TP 1/1.5/2/3R (4); BE+trailing without final TP (3×4×3=36); fixed TP+fixed-distance trailing (4×110=440); time exit 15/30/60/120 bars (4). Partial close excluded because volume/fill semantics remain undefined.

Fixed-distance levels are absolute XAU price units, converted to R per trade; point is metadata only. Activation zero begins after the first completed post-entry bar. Entry bar excluded; stop updates apply next bar; M1 gaps and conflicting same-bar events are ambiguous/no fill. Costs are not modeled. Ranking is discovery-only, not a production recommendation or Fresh Holdout.

## Run
Pull the branch into a dedicated clean worktree, then run this command with the frozen paths from the checkpoint:

    python scripts/run_sp2l_v3_unified_management_matrix.py --m1-csv PATH_TO_FROZEN_M1_CSV --entry-csv PATH_TO_FROZEN_ENTRY_CSV --point 0.01 --contract-size 100 --volume 0.01 --output-dir NEW_NONEXISTENT_OUTPUT_DIRECTORY
