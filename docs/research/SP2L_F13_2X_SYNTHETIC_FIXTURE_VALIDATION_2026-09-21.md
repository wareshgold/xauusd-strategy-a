# F13 2X Synthetic Fixture Gate Validation — 2026-09-21

## Result

**PASS**

Commit validated: `99502b075475ec896a994951a47b415d385c9349`  
GitHub Actions run: **#186** (`35574730309`)  
Validation job: **success**

## Coverage

- 15 deterministic F13 fixture classes.
- 50% Entry-to-SL relationship tested for bullish and bearish price layouts.
- Non-50% relationship rejection tested.
- Unresolved lifecycle variants remain explicitly unresolved.
- Canonical eligibility remains false for every fixture.
- Production eligibility remains false for every fixture.

## Safety

This gate does not resolve:
- order type;
- trigger event;
- fill semantics;
- 2X activation policy;
- TP allocation;
- shared/separate SL;
- entry/SL update precedence.

No canonical geometry or production behavior was changed.

## Gate disposition

F13 synthetic fixture gate: **PASS**  
F13 executable source resolution: **BLOCKED / PARTIAL**  
Frozen Geometry: **BLOCKED**  
Forward Test: **UNTOUCHED**
