from __future__ import annotations

from .models import GateResult, GateStatus, Stage


def source_gate(*, source_resolved: bool, unresolved_items: list[str]) -> GateResult:
    if not source_resolved:
        return GateResult(
            name=Stage.STRATEGY_LAB.value,
            status=GateStatus.BLOCKED,
            evidence="Source resolution is incomplete.",
            details={"unresolved_items": unresolved_items},
        )
    return GateResult(
        name=Stage.STRATEGY_LAB.value,
        status=GateStatus.PASS,
        evidence="Source resolution is complete.",
        details={"unresolved_items": []},
    )


def code_gate(*, fixtures_passed: int, fixtures_total: int, code_revision: str) -> GateResult:
    if fixtures_total <= 0 or fixtures_passed != fixtures_total:
        return GateResult(
            name=Stage.STRATEGY_ENGINE.value,
            status=GateStatus.BLOCKED,
            evidence="Strategy code is not fixture-complete.",
            details={
                "fixtures_passed": fixtures_passed,
                "fixtures_total": fixtures_total,
                "code_revision": code_revision,
            },
        )
    return GateResult(
        name=Stage.STRATEGY_ENGINE.value,
        status=GateStatus.PASS,
        evidence="All registered fixtures pass.",
        details={
            "fixtures_passed": fixtures_passed,
            "fixtures_total": fixtures_total,
            "code_revision": code_revision,
        },
    )


def validation_gate(
    *,
    development_pass: bool,
    untouched_validation_pass: bool,
    robustness_pass: bool,
    fresh_holdout_pass: bool,
) -> GateResult:
    checks = {
        "development": development_pass,
        "untouched_validation": untouched_validation_pass,
        "robustness": robustness_pass,
        "fresh_holdout": fresh_holdout_pass,
    }
    if not all(checks.values()):
        return GateResult(
            name=Stage.TEST_FACTORY.value,
            status=GateStatus.BLOCKED,
            evidence="Required statistical validation gates are incomplete.",
            details=checks,
        )
    return GateResult(
        name=Stage.TEST_FACTORY.value,
        status=GateStatus.PASS,
        evidence="All required statistical validation gates pass.",
        details=checks,
    )


def forward_gate(*, python_mt5_reconciled: bool, forward_pass: bool) -> GateResult:
    if not python_mt5_reconciled or not forward_pass:
        return GateResult(
            name=Stage.FORWARD_VALIDATION.value,
            status=GateStatus.BLOCKED,
            evidence="Forward validation is not production-eligible.",
            details={
                "python_mt5_reconciled": python_mt5_reconciled,
                "forward_pass": forward_pass,
            },
        )
    return GateResult(
        name=Stage.FORWARD_VALIDATION.value,
        status=GateStatus.PASS,
        evidence="Forward validation and reconciliation pass.",
        details={
            "python_mt5_reconciled": python_mt5_reconciled,
            "forward_pass": forward_pass,
        },
    )
