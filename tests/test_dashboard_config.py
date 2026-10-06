from pathlib import Path
import json
import pytest

from strategy_factory.dashboard_config import (
    DashboardConfigError,
    ForwardConfig,
    ResearchConfig,
    apply_settings,
    build_config,
    default_config,
    load_config,
    save_config,
)


def test_default_config_is_valid_and_deterministic():
    cfg = default_config()
    cfg.validate()
    assert cfg.fingerprint
    assert cfg.apply_mode == "STAGED_FORWARD_CONFIG"


def test_save_and_load_round_trip(tmp_path: Path):
    path = tmp_path / "dashboard_config.json"
    cfg = build_config(
        revision="R2",
        research=ResearchConfig(tp_r=3.0),
        forward=ForwardConfig(trail_distance_price=0.05),
    )
    save_config(path, cfg)
    assert load_config(path) == cfg


def test_tampered_config_is_rejected(tmp_path: Path):
    path = tmp_path / "dashboard_config.json"
    cfg = default_config()
    save_config(path, cfg)
    payload = json.loads(path.read_text())
    payload["forward"]["trail_distance_price"] = 9.0
    path.write_text(json.dumps(payload))
    with pytest.raises(DashboardConfigError, match="fingerprint"):
        load_config(path)


def test_invalid_values_are_rejected():
    with pytest.raises(DashboardConfigError):
        build_config(
            revision="BAD",
            research=ResearchConfig(tp_r=0),
            forward=ForwardConfig(),
        ).validate()


def test_apply_settings_is_staged_only(tmp_path: Path):
    path = tmp_path / "dashboard_config.json"
    cfg = apply_settings(
        path,
        research=ResearchConfig(tp_r=2.0),
        forward=ForwardConfig(trail_activation_price=0.15),
        revision="APPLY-1",
    )
    assert load_config(path) == cfg
    assert cfg.apply_mode == "STAGED_FORWARD_CONFIG"
