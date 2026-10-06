import pytest

from strategy_factory.compiler import CompilationBlocked, StrategyCompiler
from strategy_factory.fixtures import FixtureExpectation, FixtureSuite, StrategyFixture
from strategy_factory.sp2l_manifest import build_sp2l_research_manifest


def test_unresolved_sp2l_manifest_cannot_compile():
    manifest = build_sp2l_research_manifest()
    with pytest.raises(CompilationBlocked):
        StrategyCompiler().compile(manifest)


def test_fixture_suite_accepts_and_rejects_deterministically():
    suite = FixtureSuite(
        [
            StrategyFixture("F001", "accepted input", {"valid": True}, FixtureExpectation.ACCEPT),
            StrategyFixture("F002", "rejected input", {"valid": False}, FixtureExpectation.REJECT),
        ]
    )

    def evaluator(data):
        if not data["valid"]:
            raise ValueError("fixture rejection")

    results = suite.run(evaluator)
    assert len(results) == 2
    assert all(result.passed for result in results)
    assert suite.passed == 2
