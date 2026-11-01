import hashlib
from datetime import datetime, timezone

import pytest

from strategy_factory.frozen_entry_population import ENTRY_FIELDS, load_frozen_entry_population


T0 = int(datetime(2026, 10, 5, tzinfo=timezone.utc).timestamp())
VARIANT = "A_TRAIL_0.40_ACTIVATED_PROXY_V3"


def row(
    direction,
    timestamp,
    *,
    setup_offset=60,
    entry_proxy="4000.0",
    sl_initial="3996.0",
    risk_price="4.0",
    exit_price="9999",
    r_multiple="88",
):
    setup = datetime.fromtimestamp(timestamp - setup_offset, timezone.utc).isoformat()
    entry = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    return [
        "A", VARIANT, direction, setup, entry,
        entry_proxy, sl_initial, "", risk_price,
        "2026-10-05T00:04:00+00:00", exit_price, "OLD_EXIT", "CLOSED", r_multiple,
    ]


def write_csv(tmp_path, rows):
    path = tmp_path / "v3_entries.csv"
    content = [",".join(ENTRY_FIELDS)] + [",".join(values) for values in rows]
    path.write_text("\n".join(content) + "\n", encoding="utf-8")
    return path


def load(path, bars):
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return load_frozen_entry_population(path, bars, sha)


def test_loader_preserves_v3_entries_and_ignores_old_exit_results(tmp_path):
    path = write_csv(tmp_path, [
        row("BUY", T0, exit_price="5000", r_multiple="100"),
        row("SELL", T0 + 60, exit_price="1", r_multiple="-100"),
    ])
    population, info = load(path, [{"time": T0}, {"time": T0 + 60}])

    assert len(population) == 2
    assert population[0]["direction"] == "BUY"
    assert population[0]["theoretical_entry"] == 4000.0
    assert population[0]["sl"] == 3996.0
    assert population[0]["risk"] == 4.0
    assert population[0]["entry_idx"] == 0
    assert population[1]["direction"] == "SELL"
    assert population[1]["entry_idx"] == 1
    assert info["rows"] == 2
    assert info["source"] == "FROZEN_V3_ENTRY_CSV"
    assert info["unique_trade_identities"] == 2
    assert info["unique_signal_identities"] == 2
    assert info["multi_trade_signal_groups"] == 0
    assert "exit_price" in info["ignored_exit_fields"]
    assert "r_multiple" in info["ignored_exit_fields"]


def test_loader_accepts_distinct_trades_sharing_one_signal(tmp_path):
    path = write_csv(tmp_path, [
        row("SELL", T0, setup_offset=180, sl_initial="4004.0", risk_price="4.0"),
        row("SELL", T0, setup_offset=60, sl_initial="4002.0", risk_price="2.0"),
    ])
    population, info = load(path, [{"time": T0}])

    assert len(population) == 2
    assert [trade["sl"] for trade in population] == [4004.0, 4002.0]
    assert info["unique_trade_identities"] == 2
    assert info["unique_signal_identities"] == 1
    assert info["multi_trade_signal_groups"] == 1
    assert info["trade_identity_fields"] == [
        "entry_time_utc", "direction", "entry_proxy", "sl_initial",
    ]


def test_loader_rejects_duplicate_trade_identity_even_if_setup_time_differs(tmp_path):
    path = write_csv(tmp_path, [
        row("BUY", T0, setup_offset=120),
        row("BUY", T0, setup_offset=60),
    ])
    with pytest.raises(ValueError, match="duplicate frozen V3 trade identity"):
        load(path, [{"time": T0}])


def test_loader_rejects_wrong_source_sha256(tmp_path):
    path = write_csv(tmp_path, [row("BUY", T0)])
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_frozen_entry_population(path, [{"time": T0}], "0" * 64)


def test_loader_rejects_entry_timestamp_missing_from_m1_dataset(tmp_path):
    path = write_csv(tmp_path, [row("BUY", T0 + 60)])
    with pytest.raises(ValueError, match="absent from the M1 dataset"):
        load(path, [{"time": T0}])


def test_loader_rejects_invalid_direction(tmp_path):
    path = write_csv(tmp_path, [row("HOLD", T0)])
    with pytest.raises(ValueError, match="invalid direction"):
        load(path, [{"time": T0}])
