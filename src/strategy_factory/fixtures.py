from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


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
        self._last_results: list[FixtureResult] = []

    def add(self, fixture: StrategyFixture) -> None:
        self.fixtures.append(fixture)

    def run(self, evaluator: Callable[[dict[str, Any]], Any]) -> list[FixtureResult]:
        results: list[FixtureResult] = []
        for fixture in self.fixtures:
            try:
                evaluator(fixture.input_data)
                actual = FixtureExpectation.ACCEPT.value
                details: dict[str, Any] = {}
            except Exception as exc:
                actual = FixtureExpectation.REJECT.value
                details = {"error": str(exc)}
            results.append(
                FixtureResult(
                    fixture.fixture_id,
                    actual == fixture.expected.value,
                    fixture.expected,
                    actual,
                    details,
                )
            )
        self._last_results = results
        return results

    @property
    def passed(self) -> int:
        return sum(result.passed for result in self._last_results)

    @property
    def total(self) -> int:
        return len(self._last_results)
