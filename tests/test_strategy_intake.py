from dataclasses import replace

import pytest

from strategy_factory.strategy_intake import (
    StrategyIntakeError,
    StrategySourceIntake,
    StrategySourcePlatform,
)


def make_intake(**changes):
    record = StrategySourceIntake(
        intake_id="YT-GOLD-001",
        platform=StrategySourcePlatform.YOUTUBE,
        source_url="https://www.youtube.com/watch?v=abcdefghijk",
        source_title="Example gold strategy",
        publisher="Example channel",
        source_revision="video:abcdefghijk",
        captured_at_utc="2026-10-13T06:00:00Z",
        snapshot_uri="artifact://strategy-intake/YT-GOLD-001/transcript.txt",
        snapshot_sha256="a" * 64,
        strategy_claims=("Entry after a confirmed breakout",),
        unresolved_questions=("Define confirmed breakout precisely",),
        extraction_notes="Claim extracted for research; not source-verified.",
    )
    return replace(record, **changes)


def test_intake_fingerprint_is_deterministic_and_source_claims_stay_noncanonical():
    record = make_intake()
    assert record.fingerprint == make_intake().fingerprint
    payload = record.as_dict()
    assert payload["canonical"] is False
    assert payload["backtest_approved"] is False
    assert payload["forward_approved"] is False
    assert payload["production_eligible"] is False
    assert payload["allowed_use"] == "RESEARCH_CANDIDATE_DRAFT_ONLY"
    assert payload["unresolved_questions"] == ["Define confirmed breakout precisely"]
    assert payload["unresolved_count"] == 1


def test_intake_supports_github_sources():
    record = make_intake(
        platform=StrategySourcePlatform.GITHUB,
        source_url="https://github.com/example-org/example-strategy/blob/0123456789abcdef0123456789abcdef01234567/strategy.py",
        source_revision="0123456789abcdef0123456789abcdef01234567",
    )
    record.validate()
    assert record.candidate_intake_ready


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("source_url", "http://www.youtube.com/watch?v=abcdefghijk", "HTTPS"),
        ("source_url", "https://example.com/strategy", "host does not match"),
        ("snapshot_sha256", "g" * 64, "lowercase hexadecimal"),
        ("captured_at_utc", "2026-10-13T10:00:00+04:00", "UTC offset"),
        ("captured_at_utc", "2026-10-13T10:00:00", "UTC offset"),
        ("strategy_claims", (), "at least one"),
        ("strategy_claims", ("same claim", "same claim"), "duplicate strategy claims"),
        ("unresolved_questions", ("same question", "same question"), "duplicate unresolved"),
    ],
)
def test_intake_fails_closed_on_invalid_provenance_or_claims(field, value, message):
    with pytest.raises(StrategyIntakeError, match=message):
        replace(make_intake(), **{field: value}).validate()


def test_fingerprint_changes_when_snapshot_bytes_change():
    original = make_intake()
    changed = replace(original, snapshot_sha256="b" * 64)
    assert original.fingerprint != changed.fingerprint


def test_unresolved_questions_do_not_turn_claims_into_canonical_rules():
    record = make_intake(
        unresolved_questions=(
            "Entry timing unclear",
            "Stop placement unclear",
            "Costs not specified",
        )
    )
    payload = record.as_dict()
    assert payload["candidate_intake_ready"] is True
    assert payload["unresolved_count"] == 3
    assert payload["canonical"] is False
    assert payload["forward_approved"] is False
