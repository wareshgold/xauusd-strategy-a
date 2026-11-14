"""Synthetic end-to-end tests for the isolated MA offline observer."""
import ast
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.research.ma_offline_observer import (
    EVIDENCE_MODE,
    INPUT_SCHEMA_VERSION,
    run_offline_observer,
)


class TestMAOfflineObserver(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input_path = self.root / "fixture.json"
        self.payload = {
            "schema_version": INPUT_SCHEMA_VERSION,
            "run_id": "offline-fixture-001",
            "process_session_id": "synthetic-session-001",
            "source_revision": "fixture-source-revision",
            "current_m1_bar_open_server_epoch": 180,
            "last_completed_m1_bar_open_server_epoch": 120,
            "last_completed_m1_bar_close_server_epoch": 180,
            "server_utc_offset_seconds": None,
            "bars_snapshot": [
                {"time": 60, "open": 1.0, "high": 2.0, "low": 0.5, "close": 1.5},
                {"time": 120, "open": 1.5, "high": 2.5, "low": 1.0, "close": 2.0},
                {"time": 180, "open": 2.0, "high": 2.2, "low": 1.8, "close": 2.1},
            ],
            "observations": [
                {
                    "candidate_id": "synthetic-candidate-001",
                    "poll_sequence": 1,
                    "trigger_time_server_epoch": 120,
                    "decision_observed_at_utc": "2026-11-14T08:00:12.345Z",
                    "decision_monotonic_ns": 987654321,
                },
                {
                    "candidate_id": "synthetic-candidate-002",
                    "poll_sequence": 2,
                    "trigger_time_server_epoch": 120,
                    "decision_observed_at_utc": "2026-11-14T08:00:13.345Z",
                    "decision_monotonic_ns": 1087654321,
                },
            ],
        }
        self._write_input()

    def tearDown(self):
        self.temp.cleanup()

    def _write_input(self):
        self.input_path.write_text(
            json.dumps(self.payload, separators=(",", ":"), ensure_ascii=False),
            encoding="utf-8",
        )

    def test_end_to_end_writes_jsonl_and_manifest_with_hashes(self):
        output = self.root / "out-001"
        manifest = run_offline_observer(input_path=self.input_path, output_dir=output)
        evidence = (output / "observations.jsonl").read_bytes()
        rows = [json.loads(line) for line in evidence.splitlines()]
        self.assertEqual(manifest["evidence_mode"], EVIDENCE_MODE)
        self.assertEqual(manifest["observation_count"], 2)
        self.assertEqual(manifest["output_sha256"], hashlib.sha256(evidence).hexdigest())
        self.assertEqual(rows[0]["observation"]["alignment_status"], "READY_FOR_RESEARCH_ALIGNMENT")
        self.assertEqual(rows[0]["observation"]["decision_observed_at_utc"], "2026-11-14T08:00:12.345Z")
        self.assertEqual(sorted(p.name for p in output.iterdir()), ["manifest.json", "observations.jsonl"])

    def test_unresolved_alignment_is_preserved_not_dropped(self):
        self.payload["last_completed_m1_bar_close_server_epoch"] = 181
        self._write_input()
        output = self.root / "out-unresolved"
        manifest = run_offline_observer(input_path=self.input_path, output_dir=output)
        rows = [json.loads(line) for line in (output / "observations.jsonl").read_text().splitlines()]
        self.assertEqual(manifest["observation_count"], 2)
        self.assertTrue(all(row["observation"]["alignment_status"] == "UNRESOLVED" for row in rows))

    def test_existing_output_directory_is_never_overwritten(self):
        output = self.root / "already-there"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("preserve", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            run_offline_observer(input_path=self.input_path, output_dir=output)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
        self.assertEqual(list(output.iterdir()), [sentinel])

    def test_duplicate_candidate_id_is_rejected_before_output_creation(self):
        self.payload["observations"][1]["candidate_id"] = self.payload["observations"][0]["candidate_id"]
        self._write_input()
        output = self.root / "out-duplicate"
        with self.assertRaises(ValueError):
            run_offline_observer(input_path=self.input_path, output_dir=output)
        self.assertFalse(output.exists())

    def test_non_increasing_poll_sequence_is_rejected(self):
        self.payload["observations"][1]["poll_sequence"] = 1
        self._write_input()
        with self.assertRaises(ValueError):
            run_offline_observer(input_path=self.input_path, output_dir=self.root / "out-sequence")

    def test_deterministic_replay_has_identical_evidence_bytes(self):
        first = self.root / "out-first"
        second = self.root / "out-second"
        run_offline_observer(input_path=self.input_path, output_dir=first)
        run_offline_observer(input_path=self.input_path, output_dir=second)
        self.assertEqual(
            (first / "observations.jsonl").read_bytes(),
            (second / "observations.jsonl").read_bytes(),
        )
        self.assertEqual(
            (first / "manifest.json").read_bytes(),
            (second / "manifest.json").read_bytes(),
        )

    def test_output_directory_cannot_be_an_ancestor_of_input(self):
        with self.assertRaises(ValueError):
            run_offline_observer(input_path=self.input_path, output_dir=self.root)

    def test_observer_has_no_forbidden_imports_or_execution_calls(self):
        source = Path(__file__).parents[1] / "scripts" / "research" / "ma_offline_observer.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        imported = []
        called = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
            elif isinstance(node, ast.Call):
                name = node.func.id if isinstance(node.func, ast.Name) else (
                    node.func.attr if isinstance(node.func, ast.Attribute) else ""
                )
                called.append(name)
        self.assertFalse(any(name == "MetaTrader5" or name.startswith("MetaTrader5.") for name in imported))
        self.assertFalse(any("run_sp2l" in name.lower() or "runner" in name.lower() for name in imported))
        forbidden_calls = {"order_send", "order_check", "positions_get", "orders_get", "subprocess"}
        self.assertFalse(forbidden_calls.intersection(called))


if __name__ == "__main__":
    unittest.main()
