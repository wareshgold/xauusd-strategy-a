"""Deterministic tests for the cross-worktree singleton runner lock."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sp2l_runner_lock import (
    RunnerLockError,
    acquire_runner_lock,
    release_runner_lock,
)


class RunnerLockTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "runner.lock"

    def tearDown(self):
        self.temp.cleanup()

    def test_atomic_create_and_release(self):
        self.assertIsNone(acquire_runner_lock(self.path, pid=111))
        self.assertEqual(json.loads(self.path.read_text())["pid"], 111)
        release_runner_lock(self.path, pid=111)
        self.assertFalse(self.path.exists())

    def test_live_owner_blocks_second_runner(self):
        self.assertIsNone(acquire_runner_lock(self.path, pid=111))
        with patch("sp2l_runner_lock._pid_is_alive", return_value=True):
            self.assertEqual(acquire_runner_lock(self.path, pid=222), 111)
        self.assertEqual(json.loads(self.path.read_text())["pid"], 111)

    def test_stale_owner_is_replaced(self):
        self.path.write_text(json.dumps({"pid": 111}))
        with patch("sp2l_runner_lock._pid_is_alive", return_value=False):
            self.assertIsNone(acquire_runner_lock(self.path, pid=222))
        self.assertEqual(json.loads(self.path.read_text())["pid"], 222)

    def test_malformed_lock_fails_closed(self):
        self.path.write_text("not-json")
        with self.assertRaises(RunnerLockError):
            acquire_runner_lock(self.path, pid=222)

    def test_lock_creation_failure_fails_closed(self):
        with patch("sp2l_runner_lock.os.open", side_effect=PermissionError("denied")):
            with self.assertRaises(RunnerLockError):
                acquire_runner_lock(self.path, pid=222)

    def test_release_does_not_remove_another_pid_lock(self):
        self.assertIsNone(acquire_runner_lock(self.path, pid=111))
        release_runner_lock(self.path, pid=222)
        self.assertTrue(self.path.exists())

    def test_dead_process_detection(self):
        with patch("sp2l_runner_lock.os.kill", side_effect=ProcessLookupError()):
            from sp2l_runner_lock import _pid_is_alive
            self.assertFalse(_pid_is_alive(999999))


if __name__ == "__main__":
    unittest.main()
