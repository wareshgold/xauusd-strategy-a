from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_v3_discovery_artifacts import AuditError, audit_run


class DiscoveryArtifactAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.stem = "SP2L_V3_CONTROLLED_DISCOVERY_TEST"
        self.dataset = self.root / "m1.csv"
        self.entry = self.root / "entries.csv"
        self.dataset.write_text("preserved M1 fixture\n", encoding="utf-8")
        self.entry.write_text("preserved entry fixture\n", encoding="utf-8")
        self.dataset_hash = hashlib.sha256(self.dataset.read_bytes()).hexdigest()
        self.entry_hash = hashlib.sha256(self.entry.read_bytes()).hexdigest()

        matrix = []
        trades = []
        for variant in ("RR1_NO_TRAIL", "RR2_NO_TRAIL"):
            matrix.append({
                "name": variant, "signals": 2, "decisive": 2, "wins": 1,
                "losses": 1, "ambiguous": 0, "gap_exposed": 0,
                "trail_exits": 0, "tp_exits": 1, "original_sl_exits": 1,
                "win_rate_decisive_pct": 50.0, "net_R": 0.0,
                "profit_factor": 1.0, "max_drawdown_R": 1.0,
                "gross_profit_usd": 1.0, "gross_loss_usd": 1.0,
                "net_profit_usd": 0.0, "avg_R_per_decisive": 0.0,
                "avg_usd_per_decisive": 0.0, "activation_pct": 0.0,
            })
            for ts, direction, entry, sl in (
                (100, "BUY", 2000.0, 1999.0),
                (160, "SELL", 2001.0, 2002.0),
            ):
                trades.append({
                    "variant": variant, "trigger_time": ts, "direction": direction,
                    "theoretical_entry": entry, "initial_sl": sl,
                })

        payload = {
            "version": "SP2L_V3_CONTROLLED_DISCOVERY_20261007",
            "research_only": True, "symbol": "XAUUSD.ecn", "timeframe": "M1",
            "window_utc": {"start": "2026-01-01T00:00:00+00:00", "end": "2026-01-02T00:00:00+00:00"},
            "bars": 2,
            "dataset_provenance": {
                "source": "M1_ARTIFACT", "artifact": str(self.dataset),
                "content_sha256": self.dataset_hash, "byte_size": self.dataset.stat().st_size,
            },
            "frozen_population": {
                "source": "FROZEN_V3_ENTRY_CSV", "artifact": str(self.entry),
                "content_sha256": self.entry_hash, "signals": 2,
                "policy": "ONE_SHARED_SIGNAL_ENTRY_POPULATION_FOR_ALL_EXIT_VARIANTS",
            },
            "discovery_grid": {"variant_count": 2},
            "matrix": matrix,
            "trades": trades,
            "execution_assumptions": {"spread_slippage_commission": "NOT_MODELED"},
            "exit_policy": {"sameBarPolicy": "AMBIGUOUS"},
        }
        self.json_path = self.root / f"{self.stem}.json"
        self.json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        summary_path = self.root / f"{self.stem}_SUMMARY.csv"
        with summary_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(matrix[0]))
            writer.writeheader()
            writer.writerows(matrix)
        trades_path = self.root / f"{self.stem}_TRADES.csv"
        with trades_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(trades[0]))
            writer.writeheader()
            writer.writerows(trades)
        json_text = self.json_path.read_bytes().decode("utf-8")
        normalized_json = json_text.replace("\r\n", "\n")
        json_hash = hashlib.sha256(normalized_json.encode("utf-8")).hexdigest()
        (self.root / f"{self.stem}_SNAPSHOT.md").write_text(
            f"JSON SHA256: {json_hash}\n", encoding="utf-8"
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_run_writes_manifest_and_compact_result(self):
        result = audit_run(self.json_path)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["variants"], 2)
        self.assertEqual(result["trades"], 4)
        manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
        self.assertEqual(manifest["audit_status"], "PASS")
        self.assertEqual(manifest["artifacts"]["trades_csv"]["rows"], 4)

    def test_accepts_windows_crlf_json_when_snapshot_binds_normalized_content(self):
        original = self.json_path.read_bytes()
        crlf = original.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        self.json_path.write_bytes(crlf)
        raw_hash = hashlib.sha256(crlf).hexdigest()
        normalized_hash = hashlib.sha256(original.replace(b"\r\n", b"\n")).hexdigest()
        self.assertNotEqual(raw_hash, normalized_hash)
        result = audit_run(self.json_path)
        manifest = json.loads(Path(result["manifest"]).read_text(encoding="utf-8"))
        artifact = manifest["artifacts"]["discovery_json"]
        self.assertEqual(artifact["sha256"], raw_hash)
        self.assertEqual(artifact["normalized_lf_sha256"], normalized_hash)

    def test_rejects_snapshot_with_wrong_normalized_json_hash(self):
        snapshot = self.root / f"{self.stem}_SNAPSHOT.md"
        snapshot.write_text("JSON SHA256: " + ("0" * 64) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(AuditError, "LF-normalized JSON content"):
            audit_run(self.json_path)

    def test_rejects_changed_dataset_hash(self):
        self.dataset.write_text("mutated M1 fixture\n", encoding="utf-8")
        with self.assertRaisesRegex(AuditError, "M1 source SHA-256"):
            audit_run(self.json_path)

    def test_rejects_inconsistent_trade_count(self):
        path = self.root / f"{self.stem}_TRADES.csv"
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows[:-1])
        with self.assertRaisesRegex(AuditError, "row count"):
            audit_run(self.json_path)

    def test_rejects_population_drift_between_variants(self):
        path = self.root / f"{self.stem}_TRADES.csv"
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        rows[-1]["trigger_time"] = "999"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        with self.assertRaisesRegex(AuditError, "same frozen entry population"):
            audit_run(self.json_path)


if __name__ == "__main__":
    unittest.main()
