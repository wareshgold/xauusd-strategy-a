from pathlib import Path
import json

from flask import Flask

import dashboard_settings as ds


def make_app(tmp_path: Path):
    app = Flask(__name__)
    old = ds.CONFIG_PATH
    ds.CONFIG_PATH = tmp_path / "dashboard_config.json"
    ds.register_dashboard_settings(app)
    return app, old


def test_settings_page_is_staged_only(tmp_path):
    app, old = make_app(tmp_path)
    try:
        client = app.test_client()
        response = client.get("/settings")
        assert response.status_code == 200
        assert b"STAGED ONLY" in response.data
        assert not (tmp_path / "dashboard_config.json").exists()
    finally:
        ds.CONFIG_PATH = old


def test_apply_stages_validated_config(tmp_path):
    app, old = make_app(tmp_path)
    try:
        client = app.test_client()
        response = client.post("/settings/apply", data={
            "p_gap_price": "1.0",
            "spike_multiplier": "1.5",
            "max_sl_distance": "10",
            "tp_r": "2",
            "trail_distance_price": "0.02",
            "trail_activation_price": "0.10",
            "volume": "0.01",
            "pending_ttl_minutes": "30",
            "order_mode": "PENDING_LIMIT_RESEARCH",
            "revision": "UI-TEST-1",
        })
        assert response.status_code == 200
        payload = json.loads((tmp_path / "dashboard_config.json").read_text())
        assert payload["revision"] == "UI-TEST-1"
        assert payload["forward"]["trail_activation_price"] == 0.1
        assert "STAGED: UI-TEST-1" in response.text
    finally:
        ds.CONFIG_PATH = old


def test_apply_rejects_invalid_config(tmp_path):
    app, old = make_app(tmp_path)
    try:
        response = app.test_client().post("/settings/apply", data={
            "p_gap_price": "1",
            "spike_multiplier": "0",
            "max_sl_distance": "10",
            "tp_r": "2",
            "trail_distance_price": "0.02",
            "trail_activation_price": "0.10",
            "volume": "0.01",
            "pending_ttl_minutes": "30",
            "order_mode": "PENDING_LIMIT_RESEARCH",
            "revision": "BAD",
        })
        assert response.status_code == 400
        assert not (tmp_path / "dashboard_config.json").exists()
    finally:
        ds.CONFIG_PATH = old
