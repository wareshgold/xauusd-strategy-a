"""Unit tests for the live journal without requiring MT5."""
from pathlib import Path

from scripts.live_journal import _csv_export


def test_csv_export_union_of_keys(tmp_path: Path):
    out = tmp_path / "signals.csv"
    _csv_export(
        [{"signal_id": "A", "direction": "BUY"}, {"signal_id": "B", "sl": 10}],
        out,
    )
    text = out.read_text(encoding="utf-8-sig")
    assert "signal_id" in text
    assert "direction" in text
    assert "sl" in text
    assert "A" in text
    assert "B" in text
