from strategy_factory.fixtures import FixtureExpectation, FixtureSuite
from strategy_factory.sp2l_fixtures import (
    build_sp2l_synthetic_fixtures,
    evaluate_sp2l_fixture,
)


def test_sp2l_synthetic_fixture_catalog_is_source_constrained():
    fixtures = build_sp2l_synthetic_fixtures()
    assert len(fixtures) == 6
    assert sum(f.expected is FixtureExpectation.ACCEPT for f in fixtures) == 2
    assert sum(f.expected is FixtureExpectation.BLOCKED for f in fixtures) == 4


def test_sp2l_synthetic_fixtures_execute_deterministically():
    suite = FixtureSuite(build_sp2l_synthetic_fixtures())
    results = suite.run(evaluate_sp2l_fixture)

    assert suite.total == 6
    assert suite.passed == 6
    assert [result.actual for result in results] == [
        "ACCEPT",
        "ACCEPT",
        "BLOCKED",
        "BLOCKED",
        "BLOCKED",
        "BLOCKED",
    ]


def test_sp2l_does_not_invent_pgap_geometry():
    fixture = next(
        item for item in build_sp2l_synthetic_fixtures()
        if item.fixture_id == "SP2L-C01-001"
    )
    assert fixture.input_data["geometry_formula_defined"] is False
    assert fixture.expected is FixtureExpectation.BLOCKED
