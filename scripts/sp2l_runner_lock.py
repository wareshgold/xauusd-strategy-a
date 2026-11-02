"""OS-backed, fail-closed singleton lock shared across runner worktrees.

The lock file is persistent metadata, not the lock itself. The OS releases the
advisory lock automatically when the owning process exits, eliminating stale
file unlink/recreate races.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO


class RunnerLockError(RuntimeError):
    """Raised when the singleton lock cannot be safely acquired."""


_HELD_LOCKS: dict[str, BinaryIO] = {}


def _lock_key(path: Path) -> str:
    return os.path.normcase(str(Path(path).resolve()))


def _try_os_lock(stream: BinaryIO) -> bool:
    """Acquire a byte-range lock on Windows or flock on POSIX, without waiting."""
    if os.name == "nt":
        import msvcrt

        stream.seek(0)
        try:
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    import fcntl

    try:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except BlockingIOError:
        return False


def _unlock_os_lock(stream: BinaryIO) -> None:
    if os.name == "nt":
        import msvcrt

        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def _read_holder_pid(path: Path) -> int:
    """Return recorded owner PID, or 0 while metadata is unavailable."""
    try:
        with path.open("rb") as stream:
            stream.seek(1)  # byte zero is exclusively locked on Windows
            payload = json.loads(stream.read().decode("utf-8"))
        pid = int(payload.get("pid", 0))
        return pid if pid > 0 else 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        # The OS lock is authoritative. Metadata can briefly be incomplete
        # while the owner writes it, so unknown ownership still fails closed.
        return 0


def acquire_runner_lock(path: Path, pid: int | None = None) -> int | None:
    """Acquire a process-lifetime OS lock; return holder PID or None on success.

    The persistent lock file is never unlinked during normal operation.
    Process death releases the OS lock automatically.
    """
    lock_path = Path(path)
    owner_pid = int(pid if pid is not None else os.getpid())
    if owner_pid <= 0:
        raise RunnerLockError("runner lock owner PID must be positive")

    stream = None
    locked = False
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(str(lock_path), os.O_RDWR | os.O_CREAT, 0o600)
        stream = os.fdopen(fd, "r+b")
        # Windows byte-range locking requires the target byte to exist.
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b" ")
            stream.flush()
            os.fsync(stream.fileno())

        if not _try_os_lock(stream):
            stream.close()
            return _read_holder_pid(lock_path)
        locked = True

        payload = {
            "pid": owner_pid,
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }
        encoded = json.dumps(payload, sort_keys=True).encode("utf-8") + bytes((10,))
        stream.seek(1)  # metadata follows the byte reserved for the OS lock
        stream.write(encoded)
        stream.truncate()
        stream.flush()
        os.fsync(stream.fileno())

        _HELD_LOCKS[_lock_key(lock_path)] = stream
        return None
    except Exception as exc:
        if stream is not None:
            if locked:
                try:
                    _unlock_os_lock(stream)
                except OSError:
                    pass
            try:
                stream.close()
            except OSError:
                pass
        if isinstance(exc, RunnerLockError):
            raise
        raise RunnerLockError(
            f"cannot acquire or persist OS runner lock; refusing to run: {exc}"
        ) from exc


def release_runner_lock(path: Path, pid: int | None = None) -> None:
    """Release only this process's held OS lock; keep the metadata file."""
    lock_path = Path(path)
    owner_pid = int(pid if pid is not None else os.getpid())
    key = _lock_key(lock_path)
    stream = _HELD_LOCKS.get(key)
    if stream is None:
        return

    try:
        with lock_path.open("rb") as metadata:
            metadata.seek(1)
            payload = json.loads(metadata.read().decode("utf-8"))
        recorded_pid = int(payload.get("pid", 0))
        if recorded_pid != owner_pid:
            raise RunnerLockError(
                f"runner lock ownership changed unexpectedly: {lock_path}"
            )
        _unlock_os_lock(stream)
    except RunnerLockError:
        raise
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        raise RunnerLockError(
            f"cannot safely release runner lock: {lock_path}"
        ) from exc
    finally:
        _HELD_LOCKS.pop(key, None)
        stream.close()
