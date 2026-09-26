# SP2L Replay Statistical Audit — 2026-09-26

## Scope
Descriptive audit of the existing 26-candidate research replay. No parameter search, no geometry changes, no timezone normalization, and no production inference.

## Results

| Metric | Value |
|---|---:|
| Candidates | 26 |
| WIN | 16 |
| LOSS | 10 |
| Decisive WR | 61.538% |
| Net R | 6R |
| Profit factor (1R/−1R) | 1.60 |

### Direction
| Direction | N | Wins | Losses | WR | Net R |
|---|---:|---:|---:|---:|---:|
| BUY | 13 | 6 | 7 | 46.15% | -1R |
| SELL | 13 | 10 | 3 | 76.92% | 7R |

## Interpretation
This sample is small (n=26). The audit is descriptive only. It does not establish a stable edge, and it does not justify changing detector geometry.

The most important reproducibility limitation remains data coverage/timestamp/execution evidence. Therefore this replay cannot be treated as an uninterrupted out-of-sample performance series.

## Consequence
No canonical rule change is supported by this audit. The next evidence gate remains exact forward/backtest reconciliation using raw trigger identifiers and independently captured wall-clock UTC.
