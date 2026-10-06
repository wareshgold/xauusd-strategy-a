from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class FixtureExpectation(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"


@dataclass(frozen=True)
class StrategyFixture:
    fixture_id: str
    description: str
    input_data: dict[str, Any]
    expected: FixtureExpectation


@dataclass(frozen=True)
class FixtureResult:
    fixture_id: str
    passed: bool
    expected: FixtureExpectation
    actual: str
    details: dict[str, Any]


class FixtureSuite:
    def __init__(self, fixtures: list[StrategyFixture] | None = None) -> None:
        self.fixtures = list(fixtures or [])

    def add(self, fixture: StrategyFixture) -> None:
        self.fixtures.append(fixture)

    def run(self, evaluator) -> list[FixtureResult]:
        results: list[FixtureResult] = []
        for fixture in self.fixtures:
            try:
                evaluator(fixture.input_data)
                actual = FixtureExpectation.ACCEPT.value
            except Exception as exc:
                actual = FixtureExpectation.REJECT.value
                results.append(
                    FixtureResult(
                        fixture.fixture_id,
                        actual == fixture.expected.value,
                        fixture.expected,
                        actual,
                        {"error": str(exc)},
                    )
                )
                continue
            results.append(
                FixtureResult(
                    fixture.fixture_id,
                    actual == fixture.expected.value,
                    fixture.expected,
                    actual,
                    {},
                )
            )
        return results

    @property
    def passed(self) -> int:
        return sum(1 for result in self._last_results if result.passed) if hasattr(self, "_last_results") else 0
