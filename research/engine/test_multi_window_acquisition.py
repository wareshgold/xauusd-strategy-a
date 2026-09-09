import json

from . import multi_window_acquisition
from .multi_window_plan import HistoricalWindow


def test_run_orchestrates_planned_chunks(monkeypatch, tmp_path):
    calls = []

    def fake_acquire(request, *, api_key, output_dir):
        calls.append((request, api_key, output_dir))

        class Artifact:
            quality_status = "PASS"
            row_count = 5
            raw_sha256 = "raw"
            normalized_sha256 = "norm"

            def fingerprint(self):
                return "artifact"

        return object(), Artifact()

    monkeypatch.setattr(multi_window_acquisition, "acquire", fake_acquire)
    windows = (
        HistoricalWindow("b", "2026-01-02T00:00:00+00:00", "2026-01-02T00:04:00+00:00"),
        HistoricalWindow("a", "2026-01-01T00:00:00+00:00", "2026-01-01T00:04:00+00:00"),
    )
    result = multi_window_acquisition.run(
        windows, symbol="XAU/USD", interval="1min", max_points=5,
        source_timezone="Australia/Sydney", api_key="SECRET", output_dir=tmp_path,
    )
    assert [c[0].start_date for c in calls] == [
        "2026-01-01T00:00:00+00:00", "2026-01-02T00:00:00+00:00"
    ]
    assert result["dataset_sha256"]
    manifest = json.loads((tmp_path / "dataset_manifest.json").read_text())
    assert manifest["source_timezone"] == "Australia/Sydney"
    assert "SECRET" not in (tmp_path / "dataset_manifest.json").read_text()
