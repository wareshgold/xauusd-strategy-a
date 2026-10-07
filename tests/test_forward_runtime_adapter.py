from __future__ import annotations

from pathlib import Path

import pytest

from strategy_factory.forward_runtime_adapter import (
    ExistingRunnerProcessResult,
    ForwardRuntimeAdapterError,
    build_existing_runner_command,
    require_runner_process_success,
    runner_process_reconciliation,
)


def test_build_existing_runner_command_points_at_real_runner(tmp_path: Path):
    runner = tmp_path / "scripts" / "run_sp2l_v3_xauusd_forward_test.py"
    runner.parent.mkdir(parents=True)
    runner.write_text("print('fixture')", encoding="utf-8")

    command = build_existing_runner_command(repo_root=tmp_path)

    assert command[0].endswith("python.exe") or command[0].endswith("python")
    assert command[1] == str(runner.resolve())


def test_missing_existing_runner_fails_closed(tmp_path: Path):
    with pytest.raises(ForwardRuntimeAdapterError, match="not found"):
        build_existing_runner_command(repo_root=tmp_path)


def test_process_reconciliation_is_observational_only():
    result = ExistingRunnerProcessResult(
        command=("python", "runner.py"),
        returncode=0,
        stdout="ok",
        stderr="",
        timed_out=False,
    )

    observed = runner_process_reconciliation(result)

    assert observed["runner_returncode"] == 0
    assert observed["runner_timed_out"] is False
    assert "observed_positions" not in observed
    assert "matched_positions" not in observed
    assert "mismatched_positions" not in observed


def test_require_runner_process_success_rejects_timeout():
    result = ExistingRunnerProcessResult(
        command=("python", "runner.py"),
        returncode=-1,
        stdout="",
        stderr="timeout",
        timed_out=True,
    )

    with pytest.raises(ForwardRuntimeAdapterError, match="timed out"):
        require_runner_process_success(result)


def test_require_runner_process_success_rejects_nonzero_exit():
    result = ExistingRunnerProcessResult(
        command=("python", "runner.py"),
        returncode=3,
        stdout="",
        stderr="boom",
        timed_out=False,
    )

    with pytest.raises(ForwardRuntimeAdapterError, match="returncode=3"):
        require_runner_process_success(result)


def test_require_runner_process_success_accepts_zero_exit():
    result = ExistingRunnerProcessResult(
        command=("python", "runner.py"),
        returncode=0,
        stdout="ok",
        stderr="",
        timed_out=False,
    )

    require_runner_process_success(result)
