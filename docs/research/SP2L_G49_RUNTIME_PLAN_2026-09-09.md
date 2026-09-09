# SP2L G49 — Historical Multi-Window Runtime Plan

Date: 2026-09-09
Status: CI/runtime planning implemented; real historical acquisition pending local execution.

## Scope

G49 extends the strategy-neutral acquisition foundation from a single 5,000-row sample to deterministic historical coverage planning. It does not define Strategy A geometry, generate BUY/SELL signals, optimize parameters, or select data based on performance.

## Runtime contract

1. Define explicit UTC historical windows.
2. Expand each window into non-overlapping provider-sized chunks.
3. Acquire each chunk independently with the existing Twelve Data adapter.
4. Preserve each raw response and provenance separately.
5. Normalize every chunk using the explicitly supplied source timezone.
6. Run the existing quality audit per chunk.
7. Reject the dataset if any chunk is structurally invalid; do not fabricate missing bars.
8. Verify chunk continuity and reject overlaps.
9. Build a deterministic dataset-level manifest from the chunk manifests and normalized coverage.

## Dataset split boundary

DEV, VAL, and FRESH_HOLDOUT boundaries must be explicit UTC ranges and immutable once the research specification enters validation. No boundary may be selected using observed trading performance.

## Current limitation

G49 provides planning and validation primitives. Real multi-window execution remains a local runtime operation because the API credential must remain outside Git and chat. G49 is not a historical-data PASS until the requested windows have actually been acquired and audited.

## Strategy boundary

Frozen Geometry remains blocked. Historical data work is infrastructure only and cannot authorize canonical Strategy A BUY/SELL detection.
