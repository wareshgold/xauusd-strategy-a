# SP2L 125R Geometry Gate — 2026-09-16

## Current status

`UNRESOLVED`

## Evidence established

The persisted 1min observation at `2026-08-20 20:54:00` is arithmetically reproducible from its persisted Entry, Stop, and TP1 values. The current implementation derives Entry from the first post-correction close reclaim and derives invalidation from the correction extreme.

## What is not established

The source has not yet been shown to uniquely require those exact OHLC anchors, nor has it established a minimum stop distance or any replacement rule for a very small Entry-to-invalidation distance.

## Gate consequence

No minimum-risk threshold, stop buffer, wick/body rule, or alternate entry formula may be introduced merely to improve the baseline statistics or eliminate the 125R observation.

Frozen Geometry therefore remains blocked until source evidence and synthetic fixtures discriminate the relevant geometry.
