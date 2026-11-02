"""Atomic, fail-closed single-runner lock shared across Git worktrees."""
from __future__ import annotations

import errno
import json
import os
from datetime import datetime, timezone
from pathlib import Path


class RunnerLockError(RuntimeError):
    """Raised when the singleton lock cannot be safely acquired."""


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        raise RunnerLockError("runner lock contains an invalid PID")
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        raise RunnerLockError(
            f"cannot verify runner-lock PID {pid}: {exc}"
        ) from exc


def acquire_runner_lock(path: Path, pid: int | None = None) -> int | None:
    """Atomically create a shared lock; return holder PID or None on success.

    A stale lock is removed only after the recorded PID is proven absent.
    Malformed or inaccessible locks fail closed.
    """
    lock_path = Path(path)
    owner_pid = int(pid if pid is not None else os.getpid())
    payload = {
        "pid": owner_pid,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    encoded = (json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")

    for _attempt in range(2):
        try:
            fd = os.open(
                str(lock_path),
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        except FileExistsError:
            try:
                current = json.loads(lock_path.read_text(encoding="utf-8"))
                holder_pid = int(current["pid"])
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                raise RunnerLockError(
                    f"existing runner lock is unreadable or malformed: {lock_path}"
                ) from exc
            if _pid_is_alive(holder_pid):
                return holder_pid
            try:
                lock_path.unlink()
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise RunnerLockError(
                    f"cannot remove proven-stale runner lock: {lock_path}"
                ) from exc
            continue
        except OSError as exc:
            raise RunnerLockError(
                f"cannot create runner lock; refusing to run without singleton protection: {exc}"
            ) from exc

        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as exc:
            try:
                lock_path.unlink()
            except OSError:
                pass
            raise RunnerLockError(
                f"cannot persist runner lock; refusing to run: {exc}"
            ) from exc
        return None

    raise RunnerLockError("runner lock changed concurrently; retry startup")


def release_runner_lock(path: Path, pid: int | None = None) -> None:
    """Remove only a lock whose recorded PID still belongs to this process."""
    lock_path = Path(path)
    owner_pid = int(pid if pid is not None else os.getpid())
    try:
        current = json.loads(lock_path.read_text(encoding="utf-8"))
        if int(current.get("pid", 0)) == owner_pid:
            lock_path.unlink()
    except FileNotFoundError:
        return
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RunnerLockError(
            f"cannot safely release runner lock: {lock_path}"
        ) from exc
