import pytest

from strategy_factory.test_contract import (
    ContractViolation,
    DatasetRole,
    ExecutionSemantics,
    HistoricalTestSpec,
    TestDataset,
    validate_test_spec,
)


def make_dataset(role: DatasetRole, immutable: bool = False) -> TestDataset:
    return TestDataset(
        dataset_id=f"{role.value}-001",
        role=role,
        data_revision="DATA-001",
        start="2026-01-01T00:00:00Z",
        end="2026-02-01T00:00:00Z",
        source="RESEARCH_FIXTURE",
        immutable=immutable,
    )


def make_spec(role: DatasetRole, immutable: bool = False) -> HistoricalTestSpec:
    return HistoricalTestSpec(
        test_id="TEST-001",
        strategy_id="SP2L-A",
        strategy_revision="STRAT-001",
        dataset=make_dataset(role, immutable),
        execution_semantics=ExecutionSemantics.TICK_FEASIBLE,
        parameters={"TP_R": 2},
    )


def test_development_dataset_is_valid_without_holdout_lock():
    spec = make_spec(DatasetRole.DEVELOPMENT)
    assert validate_test_spec(spec).is_holdout is False


@pytest.mark.parametrize(
    "role",
    [DatasetRole.UNTOUCHED_VALIDATION, DatasetRole.FRESH_HOLDOUT],
)
def test_validation_and_holdout_require_immutable_data(role):
    with pytest.raises(ContractViolation):
        validate_test_spec(make_spec(role, immutable=False))


def test_holdout_is_explicit_and_serializable():
    spec = make_spec(DatasetRole.FRESH_HOLDOUT, immutable=True)
    result = validate_test_spec(spec)
    assert result.is_holdout is True
    assert result.as_dict()["dataset"]["role"] == "FRESH_HOLDOUT"


def test_dataset_identity_and_order_are_required():
    bad = TestDataset(
        dataset_id="",
        role=DatasetRole.DEVELOPMENT,
        data_revision="DATA-001",
        start="2026-02-01T00:00:00Z",
        end="2026-01-01T00:00:00Z",
        source="RESEARCH_FIXTURE",
    )
    with pytest.raises(ContractViolation):
        bad.validate()
