# Research System Checkpoint

## Git state

- Branch: `research/entry-edge-post-entry-path`
- Pre-snapshot checkpoint: `23ae948`
- Snapshot commit: `38bd87f440daa911d56b0eb8823ca514f19bb336`
- Scope: research infrastructure and documentation only
- Production Strategy A: unchanged
- Fresh Holdout: unchanged

## Workflow state

The new GitHub Actions research workflow is operational.

Successful run:
- Run ID: `33949830517`
- Workflow: `Research - DELAY1 conditional path information v2`
- Commit: `23ae948`
- Artifact ID: `9964463686`
- Artifact: `delay1-conditional-path-information-v2`
- Artifact digest: `sha256:96e17016ed6a2192fd4736c2a3f6d335f4c5ee2889e765970ea9cc1bf339426a`

## Research system architecture

```text
Historical OHLC data
        ↓
Deterministic Strategy A reconstruction
        ↓
Research hypothesis script
        ↓
DEV / VAL chronological split
        ↓
Statistical diagnostics
        ↓
GitHub Actions reproducible run
        ↓
JSON artifact
        ↓
Human/AI statistical interpretation
        ↓
Hypothesis decision
        ↓
Fresh Holdout evaluation only after freeze
        ↓
Promotion or rejection
```

## Why this is faster

The main speed improvement is workflow throughput, not a claim that the underlying calculations are intrinsically faster.

Benefits:
- reproducible execution
- no manual local execution required for every run
- machine-readable artifacts
- easy reruns from a known commit
- research can be separated from production
- independent hypotheses can be executed as separate Actions
- results can be compared without copying ad-hoc terminal output

## Current strongest research lead

5m post-entry adverse-excursion behavior is the strongest current diagnostic lead.

The latest conditional-path research shows stable negative Spearman association between MAE checkpoints and final R, approximately:

- T1 MAE: -0.507
- T2 MAE: -0.585
- T3 MAE: -0.564

This is a research finding, not a production rule.

## Known limitation

The current partial-Spearman output is not accepted as proof of incremental information because T2/T3 partial values matched marginal values in the produced artifact.

The next implementation must use a verified nested/conditional model comparison before claiming:

`T2 adds information beyond T1`

or

`T3 adds information beyond T1 + T2`.

## Non-negotiable research controls

1. No Fresh Holdout use during discovery.
2. No production Strategy A edits from diagnostic results.
3. No arbitrary threshold hunting.
4. No hindsight leakage.
5. No promotion from DEV alone.
6. Same-candle ambiguity remains conservative.
7. Every promoted rule must survive chronological validation and Fresh Holdout evaluation.

## Next checkpoint target

Implement and validate proper nested conditional information analysis, then run it through GitHub Actions and inspect the generated artifact before any further strategy decision.
