import pytest

from strategy_factory.sp2l_discrimination import (
    DiscriminationFixture,
    FixtureDisposition,
    build_sp2l_discrimination_fixtures,
)


def test_discrimination_fixture_registry_is_deterministic():
    first = [item.as_dict() for item in build_sp2l_discrimination_fixtures()]
    second = [item.as_dict() for item in build_sp2l_discrimination_fixtures()]
    assert first == second


def test_discrimination_fixtures_require_competing_alternatives():
    with pytest.raises(ValueError):
        DiscriminationFixture(
            fixture_id="X",
            question_id="Q",
            description="test",
            alternatives=("ONLY_ONE",),
        ).validate()


def test_sp2l_fixtures_remain_blocked_until_source_discriminates():
    fixtures = build_sp2l_discrimination_fixtures()
    assert fixtures
    assert all(
        fixture.expected_disposition is FixtureDisposition.BLOCKED
        for fixture in fixtures
    )


def test_required_source_questions_have_discrimination_fixtures():
    fixtures = build_sp2l_discrimination_fixtures()
    questions = {item.question_id for item in fixtures}
    assert "SP2L.PGAP.Q1" in questions
    assert "SP2L.F12.Q1" in questions
    assert "SP2L.F12.Q2" in questions
    assert "SP2L.F10.Q1" in questions
    assert "SP2L.C06.Q1" in questions
    assert "SP2L.F14.Q1" in questions
    assert "SP2L.F14.Q2" in questions
    assert "SP2L.TP.Q1" in questions
    assert "SP2L.TP.Q2" in questions
