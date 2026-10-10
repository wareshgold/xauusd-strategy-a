from strategy_factory.run_contract import FactoryRunContract


def test_factory_run_contract_identity():
    run = FactoryRunContract.create(
        run_id="RUN-001",
        git_sha="abc123",
        dataset_identity="DATASET-X",
        strategy_revision="FROZEN-A",
    )

    data = run.to_dict()

    assert data["run_id"] == "RUN-001"
    assert data["git_sha"] == "abc123"
    assert data["dataset_identity"] == "DATASET-X"
    assert data["strategy_revision"] == "FROZEN-A"
