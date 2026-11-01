# V3 Exit Discovery robustness audit

This is a deterministic, research-only follow-on to the local V3 Discovery artifact audit. It reads the audited evidence manifest and the byte-preserved Trades CSV; it never rewrites those source files.

## Run on the preserved local run

Use the same Python environment and manifest produced by `audit_v3_discovery_artifacts.py`:

```powershell
$python = "D:\Mirzaei\Private\1\xauusd-strategy-a\.venv\Scripts\python.exe"
$manifest = "D:\Mirzaei\Private\1\sp2l-evidence\development\v3-exit-discovery-20261101\SP2L_V3_CONTROLLED_DISCOVERY_20261101T063522785317Z_EVIDENCE_MANIFEST.json"
$out = "D:\Mirzaei\Private\1\sp2l-evidence\development\v3-exit-discovery-20261101\robustness_20261101"

& $python scripts\audit_v3_exit_robustness.py --manifest $manifest --output-dir $out --bootstrap-iterations 2000 --seed 20261101 2>&1 | Tee-Object -Variable result
$exitCode = $LASTEXITCODE
$result
"ROBUSTNESS_EXIT=$exitCode"
@($result) + "ROBUSTNESS_EXIT=$exitCode" | Set-Clipboard
```

The output directory must not already exist. The script fails closed rather than overwriting a prior run. Preserve the full console output and all three generated files.

## Analyses

- Four equal-width chronological slices based on the frozen trigger-time range. Each variant reports decisive outcomes, ambiguous outcomes, unresolved/open outcomes, net R, mean R per decisive trade, win rate, profit factor, drawdown, and gap exposure per slice.
- Local parameter neighbourhood: immediate adjacent grid coordinates in RR, activation points, and trailing distance. The no-trailing controls remain isolated; they are not treated as a neighbouring point in trailing parameter space.
- Circular moving-block max-t bootstrap: UTC daily net-R vectors are resampled in contiguous circular blocks (block length is selected deterministically as max(2, round(number_of_days^(1/3)))). The same sampled day blocks are used across all 288 variants. Each variant's daily series is centered under the null, and the bootstrap maximum t-statistic is compared with the observed maximum. This is an exploratory family-wise multiplicity diagnostic for the 288-way search.

## Interpretation limits

- This is still the same development sample used to inspect all 288 variants. It is not untouched validation and not a Fresh Holdout.
- The moving-block bootstrap preserves short sequences of daily dependence, but its deterministic block length cannot represent every regime shift or long-memory dependence; it is not a formal guarantee.
- Open/unresolved rows are retained as non-decisive and never assigned a fabricated return. Explicitly ambiguous rows remain separate.
- Existing M1 gaps, same-bar ambiguity, OHLC proxy limitations, and omitted spread/slippage/commission remain applicable.
- The report sorts variants for inspection only. It does not declare a winner, freeze canonical geometry, or authorize production decisions.


## Follow-up correction: unresolved daily observations

The initial local run exposed a missing-value bug in daily matrix construction: an unresolved row with `realized_R=None` reached `float(None)`. The corrected implementation treats a variant/day as unknown if any outcome triggered on that day is ambiguous or unresolved. Such a day remains `None` through the common-block bootstrap and is excluded from that variant's observed and resampled t-statistic; it is never imputed as zero. A calendar day with no triggered rows for a variant remains a genuine zero-return day. Variants with fewer than three known daily observations are excluded from the max-t family and explicitly counted. Regression tests cover unresolved, ambiguous, no-signal, and bootstrap missingness behavior. This correction remains research-only and does not change source trade rows or the canonical Strategy A rules.
