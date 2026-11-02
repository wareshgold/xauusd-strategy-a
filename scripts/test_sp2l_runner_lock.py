"""Deterministic OS-lock tests, including real process contention/recovery."""
from __future__ import annotations

import json
import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path

from sp2l_runner_lock import (
    RunnerLockError,
    acquire_runner_lock,
    release_runner_lock,
)


def _lock_holder(path: str, ready, keep_alive) -> None:
    acquired = acquire_runner_lock(Path(path))
    ready.put((acquired is None, os.getpid()))
    keep_alive.wait(30)
    if acquired is None:
        release_runner_lock(Path(path))


def _lock_contender(path: str, result) -> None:
    holder = acquire_runner_lock(Path(path))
    result.put(holder)
    if holder is None:
        release_runner_lock(Path(path))


class RunnerLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "runner.lock"

    def tearDown(self):
        # The lock file is intentionally persistent; only remove the test dir.
        self.temp.cleanup()

    def test_os_lock_acquire_and_release_keeps_metadata_file(self):
        self.assertIsNone(acquire_runner_lock(self.path, pid=os.getpid()))
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(payload["pid"], os.getpid())
        release_runner_lock(self.path, pid=os.getpid())
        self.assertTrue(self.path.exists())
        self.assertIsNone(acquire_runner_lock(self.path, pid=os.getpid()))
        release_runner_lock(self.path, pid=os.getpid())

    def test_second_process_is_blocked_then_acquires_after_owner_dies(self):
        ctx = multiprocessing.get_context("spawn")
        ready = ctx.Queue()
        result = ctx.Queue()
        keep_alive = ctx.Event()
        owner = ctx.Process(
            target=_lock_holder, args=(str(self.path), ready, keep_alive)
        )
        contender = None
        owner.start()
        try:
            acquired, owner_pid = ready.get(timeout=15)
            self.assertTrue(acquired)
            self.assertGreater(owner_pid, 0)

            contender = ctx.Process(
                target=_lock_contender, args=(str(self.path), result)
            )
            contender.start()
            holder_pid = result.get(timeout=15)
            contender.join(timeout=15)
            self.assertFalse(contender.is_alive())
            self.assertEqual(holder_pid, owner_pid)

            owner.terminate()
            owner.join(timeout=15)
            self.assertFalse(owner.is_alive())

            # Process termination releases the OS lock without stale-file
            # unlinking; this process can now acquire the persistent lock file.
            self.assertIsNone(acquire_runner_lock(self.path, pid=os.getpid()))
            release_runner_lock(self.path, pid=os.getpid())
        finally:
            if contender is not None and contender.is_alive():
                contender.terminate()
                contender.join(timeout=5)
            if owner.is_alive():
                owner.terminate()
                owner.join(timeout=5)

    def test_invalid_pid_fails_closed(self):
        with self.assertRaises(RunnerLockError):
            acquire_runner_lock(self.path, pid=0)

    def test_release_without_owned_lock_is_noop(self):
        release_runner_lock(self.path, pid=os.getpid())
        self.assertFalse(self.path.exists())

    def test_lock_path_creation_failure_fails_closed(self):
        blocked_parent = Path(self.temp.name) / "regular-file"
        blocked_parent.write_text("x", encoding="utf-8")
        with self.assertRaises(RunnerLockError):
            acquire_runner_lock(blocked_parent / "runner.lock")


if __name__ == "__main__":
    unittest.main()
