from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sp2l_runner_provenance import (
    ProvenanceEventLog,
    make_run_identity,
    mt5_comment_token,
    position_linked,
    run_started,
    verify_event_log,
    write_run_manifest,
    validate_run_identity,
)


class RunnerProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.config = {
            "symbol": "XAUUSD.ecn",
            "timeframe": "M1",
            "tp_r": 4.0,
            "trail_activation_price": 0.4,
            "trail_distance_price": 0.4,
            "order_mode": "PENDING_LIMIT_RESEARCH",
        }
        self.identity = make_run_identity(
            runner_id="SP2L_V3_1_XAUUSD",
            runner_version="SP2L_V3_1_XAUUSD_RR4_ACT40_TRAIL40_20261101",
            git_commit="7cd57892de63773db24809cb98bedba93df8f5f0",
            config=self.config,
            run_id="0123456789abcdef0123456789abcdef",
            started_at_utc="2026-11-18T12:00:00Z",
        )

    def test_config_hash_is_key_order_independent(self):
        reordered = dict(reversed(list(self.config.items())))
        other = make_run_identity(
            runner_id="SP2L_V3_1_XAUUSD",
            runner_version="v1",
            git_commit="7cd57892de63773db24809cb98bedba93df8f5f0",
            config=reordered,
            run_id="1123456789abcdef0123456789abcdef",
        )
        self.assertEqual(self.identity["config_hash_sha256"], other["config_hash_sha256"])

    def test_changed_config_changes_hash(self):
        changed = {**self.config, "tp_r": 2.0}
        other = make_run_identity(
            runner_id="SP2L_V3_1_XAUUSD",
            runner_version="v1",
            git_commit="7cd57892de63773db24809cb98bedba93df8f5f0",
            config=changed,
            run_id="2123456789abcdef0123456789abcdef",
        )
        self.assertNotEqual(self.identity["config_hash_sha256"], other["config_hash_sha256"])

    def test_comment_is_short_correlation_hint(self):
        token = mt5_comment_token(self.identity)
        self.assertEqual(token, "S2L:01234567:" + self.identity["config_hash_sha256"][:8])
        self.assertLessEqual(len(token), 31)

    def test_manifest_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.json"
            write_run_manifest(path, self.identity)
            with self.assertRaises(FileExistsError):
                write_run_manifest(path, self.identity)
            self.assertEqual(json.loads(path.read_text())["config_hash_sha256"], self.identity["config_hash_sha256"])

    def test_run_and_position_events_verify(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = ProvenanceEventLog(Path(tmp) / "events.jsonl")
            run_started(log, self.identity)
            position_linked(
                log, self.identity, position_id=123456, symbol="XAUUSD.ecn",
                magic=26092301, order_ticket=123, deal_ticket=456,
                broker_comment=mt5_comment_token(self.identity),
            )
            result = verify_event_log(log.path)
            self.assertTrue(result["valid"])
            self.assertEqual(result["event_count"], 2)

    def test_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = ProvenanceEventLog(Path(tmp) / "events.jsonl")
            run_started(log, self.identity)
            raw = log.path.read_text()
            log.path.write_text(raw.replace("SP2L_V3_1_XAUUSD", "SP2L_TAMPERED"))
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                verify_event_log(log.path)

    def test_truncated_tail_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = ProvenanceEventLog(Path(tmp) / "events.jsonl")
            run_started(log, self.identity)
            with log.path.open("a") as stream:
                stream.write('{"broken":')
            with self.assertRaisesRegex(ValueError, "truncated"):
                verify_event_log(log.path)


    def test_multiple_appends_keep_contiguous_sequence(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = ProvenanceEventLog(Path(tmp) / "events.jsonl")
            run_started(log, self.identity)
            position_linked(
                log, self.identity, position_id=123456, symbol="XAUUSD.ecn",
                magic=26092301,
            )
            log.append("POSITION_CLOSED", {"position_id": 123456, "net": 1.25})
            result = verify_event_log(log.path)
            self.assertEqual(result["event_count"], 3)

    def test_invalid_non_finite_config_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-finite"):
            make_run_identity(
                runner_id="SP2L", runner_version="v1",
                git_commit="7cd57892de63773db24809cb98bedba93df8f5f0",
                config={"tp_r": float("nan")},
            )

    def test_invalid_git_commit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "git_commit"):
            make_run_identity(
                runner_id="SP2L", runner_version="v1",
                git_commit="not-a-commit", config={},
            )

    def test_existing_corrupt_json_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text('{"bad":true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid provenance sequence"):
                verify_event_log(path)


    def test_nested_config_is_copied_into_snapshot(self):
        original = {"risk": {"tp_r": 4.0}}
        identity = make_run_identity(
            runner_id="SP2L", runner_version="v1",
            git_commit="7cd57892de63773db24809cb98bedba93df8f5f0",
            config=original,
        )
        original["risk"]["tp_r"] = 2.0
        validate_run_identity(identity)
        self.assertEqual(identity["config_snapshot"]["risk"]["tp_r"], 4.0)

    def test_mutated_identity_snapshot_is_rejected(self):
        identity = dict(self.identity)
        identity["config_snapshot"] = dict(self.identity["config_snapshot"])
        identity["config_snapshot"]["tp_r"] = 3.0
        with self.assertRaisesRegex(ValueError, "no longer matches"):
            validate_run_identity(identity)

    def test_non_object_event_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            path.write_text('[]\\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid provenance record"):
                verify_event_log(path)


if __name__ == "__main__":
    unittest.main()
