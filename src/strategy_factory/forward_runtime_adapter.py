from __future__ import annotations

"""Research-only adapter for the existing SP2L demo forward runner.

This module deliberately does not define Strategy A geometry and does not
generate trading decisions. It only supplies a deterministic process boundary
around the already-existing forward runner so the Factory runtime bridge can
bind a frozen session to the real runner without rewriting that runner.

The adapter is intentionally small:
- command construction is explicit and auditable;
- the existing runner remains the owner of execution behavior;
- the subprocess result is observational telemetry;
- no profitability or promotion decision is made here.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
from typing import Mapping, Sequence


class ForwardRuntimeAdapterError(RuntimeError):
    """Raised when the existing forward runner cannot be launched safely."""


@dataclass(frozen=True)
class ExistingRunnerProcessResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


def build_existing_runner_command(
    *,
    repo_root: Path,
    runner_relative_path: str = "scripts/run_sp2l_v3_xauusd_forward_test.py",
) -> tuple[str, ...]:
    """Build the exact Python command for the existing real forward runner."""
    runner = (repo_root / runner_relative_path).resolve()
    if not runner.is_file():
        raise ForwardRuntimeAdapterError(
            f"existing forward runner not found: {runner}"
        )
    return (sys.executable, str(runner))


def run_existing_forward_runner(
    *,
    repo_root: Path,
    duration_seconds: int,
    env_overrides: Mapping[str, str] | None = None,
    runner_relative_path: str = "scripts/run_sp2l_v3_xauusd_forward_test.py",
) -> ExistingRunnerProcessResult:
    """Run the existing runner for a bounded demo-forward interval.

    The runner itself remains responsible for MT5 execution. This adapter only
    supplies FORWARD_TEST_SECONDS and captures process telemetry. A non-zero
    runner exit is returned as observed evidence rather than converted into a
    trading decision.
    """
    if duration_seconds <= 0:
        raise ForwardRuntimeAdapterError("duration_seconds must be positive")

    command = build_existing_runner_command(
        repo_root=repo_root,
        runner_relative_path=runner_relative_path,
    )
    env = os.environ.copy()
    env["FORWARD_TEST_SECONDS"] = str(int(duration_seconds))
    if env_overrides:
        env.update({str(k): str(v) for k, v in env_overrides.items()})

    try:
        completed = subprocess.run(
            command,
            cwd=str(repo_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=int(duration_seconds) + 30,
            check=False,
        )
        return ExistingRunnerProcessResult(
            command=command,
            returncode=int(completed.returncode),
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
        )
    except subprocess.TimeoutExpired as exc:
        return ExistingRunnerProcessResult(
            command=command,
            returncode=-1,
            stdout=(
                exc.stdout.decode(errors="replace")
                if isinstance(exc.stdout, bytes)
                else (exc.stdout or "")
            ),
            stderr=(
                exc.stderr.decode(errors="replace")
                if isinstance(exc.stderr, bytes)
                else (exc.stderr or "")
            ),
            timed_out=True,
        )


def runner_process_reconciliation(
    result: ExistingRunnerProcessResult,
) -> dict[str, object]:
    """Map process facts into the Factory's required observed-fields contract.

    This is process-level evidence only. MT5 position matching is intentionally
    not fabricated from an exit code, so observed position counts are left to a
    separate broker-observation adapter.
    """
    if result.timed_out:
        detail = "existing forward runner exceeded adapter timeout"
    elif result.returncode == 0:
        detail = "existing forward runner exited normally"
    else:
        detail = f"existing forward runner exited with returncode={result.returncode}"

    return {
        "runner_returncode": result.returncode,
        "runner_timed_out": result.timed_out,
        "runner_command": list(result.command),
        "runner_stdout_bytes": len(result.stdout.encode("utf-8", errors="replace")),
        "runner_stderr_bytes": len(result.stderr.encode("utf-8", errors="replace")),
        "detail": detail,
    }


def require_runner_process_success(
    result: ExistingRunnerProcessResult,
) -> None:
    """Fail closed for callers that require a completed bounded runner."""
    if result.timed_out:
        raise ForwardRuntimeAdapterError(
            "existing forward runner timed out before bounded session completion"
        )
    if result.returncode != 0:
        raise ForwardRuntimeAdapterError(
            f"existing forward runner failed with returncode={result.returncode}"
        )


def run_existing_forward_runner_dry_run(
    *,
    duration_seconds: int,
    env_overrides: Mapping[str, str] | None = None,
) -> ExistingRunnerProcessResult:
    """Exercise the adapter process boundary without touching MT5.

    This is a Factory integration-test primitive only. It deliberately runs a
    tiny local Python child process instead of the real SP2L runner, so a
    dry-run can prove subprocess wiring without creating/modifying/cancelling
    orders.
    """
    if duration_seconds <= 0:
        raise ForwardRuntimeAdapterError("duration_seconds must be positive")

    command = (
        sys.executable,
        "-c",
        (
            "import os; "
            "print('SP2L_FACTORY_DRY_RUN=1'); "
            "print('FORWARD_TEST_SECONDS=' + os.environ['FORWARD_TEST_SECONDS'])"
        ),
    )
    env = os.environ.copy()
    env["FORWARD_TEST_SECONDS"] = str(int(duration_seconds))
    if env_overrides:
        env.update({str(k): str(v) for k, v in env_overrides.items()})

    completed = subprocess.run(
        command,
        env=env,
        capture_output=True,
        text=True,
        timeout=int(duration_seconds) + 5,
        check=False,
    )
    return ExistingRunnerProcessResult(
        command=command,
        returncode=int(completed.returncode),
        stdout=completed.stdout,
        stderr=completed.stderr,
        timed_out=False,
    )
