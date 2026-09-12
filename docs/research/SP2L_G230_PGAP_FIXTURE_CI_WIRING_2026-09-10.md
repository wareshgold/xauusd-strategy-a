# SP2L G230 — P-Gap Fixture CI Wiring

**Date:** 2026-09-10  
**Gate:** SYNTHETIC FIXTURES  
**Status:** `CI_WORKFLOW_ADDED_RUN_PENDING`

## Objective

Ensure the G228 research-only P-Gap synthetic tests are actually executed by CI.

## Finding

The existing `research-engine-tests.yml` workflow runs only `research/engine` tests. Because G228 lives under `research/fixtures`, adding the fixture tests alone did not guarantee CI execution.

## Change

Added:

`.github/workflows/research-pgap-fixtures.yml`

The workflow is scoped to changes in `research/fixtures/**`, the research requirements file, or the workflow itself, and runs:

`python -m pytest -q research/fixtures/test_sp2l_pgap_synthetic_fixtures_g228.py`

with Python 3.12 and the pinned research dependencies.

## Validation boundary

The workflow only validates deterministic research fixtures. It does **not**:

- freeze P-Gap geometry;
- promote H1/H2 to canonical Strategy A;
- introduce generic FVG logic;
- authorize bearish geometry;
- run historical optimization;
- generate BUY/SELL decisions.

## CI status

The workflow definition is present and verified at commit `4fad50ee4dd3fff693455c7c7234e0665eedc035`. A workflow run must be observed and its result inspected before recording a CI PASS.

## Gate impact

- Source Resolution: **BLOCKED**
- Synthetic Fixtures: **IMPLEMENTED; CI RUN PENDING**
- Frozen Geometry: **BLOCKED**
- DEV/VAL/Production: **UNCHANGED / NOT AUTHORIZED**
