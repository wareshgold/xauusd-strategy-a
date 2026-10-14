from __future__ import annotations

from pathlib import Path

import pytest

from scripts.acquire_xauusd_tick_bidask import (
    acquisition_output_paths,
    ensure_acquisition_outputs_absent,
)


def test_acquisition_paths_are_explicit_and_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "xauusd.csv.gz"

    final_path, partial_path, manifest_path = acquisition_output_paths(output)

    assert final_path == output
    assert partial_path == tmp_path / "xauusd.csv.gz.partial"
    assert manifest_path == tmp_path / "xauusd.manifest.json"


def test_preflight_allows_only_a_fresh_output_set(tmp_path: Path) -> None:
    output = tmp_path / "xauusd.csv.gz"

    assert ensure_acquisition_outputs_absent(output) == acquisition_output_paths(output)


@pytest.mark.parametrize("occupied_index", [0, 1, 2], ids=["final", "partial", "manifest"])
def test_preflight_refuses_any_existing_artifact_without_changing_it(
    tmp_path: Path, occupied_index: int
) -> None:
    output = tmp_path / "xauusd.csv.gz"
    paths = acquisition_output_paths(output)
    existing = paths[occupied_index]
    existing.write_bytes(b"preserve-me")

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        ensure_acquisition_outputs_absent(output)

    assert existing.read_bytes() == b"preserve-me"
