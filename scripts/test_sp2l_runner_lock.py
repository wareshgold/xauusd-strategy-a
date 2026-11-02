"""Deterministic OS-lock tests, including real process contention/recovery."""
from __future__ import annotations

import json
import multiprocessing
import os
import tempfile
import time
import unittest
from pathlib import Path

from sp2l_runner_lock import (
    RunnerLockError,
    acquire_runner_lock,
    release_runner_lock,
)


def _lock_holder(path: str, ready, release) -> None:
    acquired = acquire_runner_lock(Path(path))
    ready.put((acquired is None, os.getpid()))
    release.wait(10)
    if acquired is None:
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

    def test_second_process_is_blocked_and_can_acquire_after_owner_dies(self):
        ctx = multiprocessing.get_context("spawn")
        ready = ctx.Queue()
        release = ctx.Event()
        owner = ctx.Process(target=_lock_holder, args=(str(self.path), ready, release))
        owner.start()
        acquired, owner_pid = ready.get(timeout=10)
        self.assertTrue(acquired)
        self.assertGreater(owner_pid, 0)

        # This process must see the live OS lock, independent of PID probes.
        holder = acquire_runner_lock(self.path, pid=os.getpid())
        self.assertIn(holder, (owner_pid, 0))

        owner.terminate()
        owner.join(timeout=10)
        self.assertFalse(owner.is_alive())

        # Process termination releases the OS lock; no stale-file unlink is
        # needed and no contender can delete a replacement lock.
        self.assertIsNone(acquire_runner_lock(self.path, pid=os.getpid()))
        release_runner_lock(self.path, pid=os.getpid())

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
