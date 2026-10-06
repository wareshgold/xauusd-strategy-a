from __future__ import annotations

from pathlib import Path
from flask import Blueprint, Response, request

from strategy_factory.dashboard_config import (
    DashboardConfigError,
    ForwardConfig,
    ResearchConfig,
    apply_settings,
    load_config,
)

settings_bp = Blueprint("dashboard_settings", __name__)
CONFIG_PATH = Path(__file__).resolve().parents[1] / "runtime" / "dashboard_config.json"


def _page(message: str = "") -> str:
    try:
        cfg = load_config(CONFIG_PATH)
    except DashboardConfigError:
        cfg = None
    if cfg is None:
        research = ResearchConfig()
        forward = ForwardConfig()
        revision = "DASHBOARD-CONFIG-1"
        fingerprint = "not yet staged"
    else:
        research = cfg.research
        forward = cfg.forward
        revision = cfg.revision
        fingerprint = cfg.fingerprint
    notice = f"<p><b>{message}</b></p>" if message else ""
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>SP2L Settings</title>
<style>body{{font-family:Consolas,monospace;background:#0e1116;color:#d8dee9;margin:24px}}
fieldset{{margin:16px 0;padding:16px;border:1px solid #2e3440}}label{{display:block;margin:8px 0}}
input{{background:#1b2129;color:#d8dee9;border:1px solid #4c566a;padding:5px;width:180px}}
button{{padding:8px 14px}}.warn{{color:#ebcb8b}}.dim{{color:#7b88a1}}</style></head>
<body><h1>SP2L Forward Settings</h1>
<p class="warn">STAGED ONLY — saving settings does not modify the running runner or place orders.</p>
{notice}
<form method="post" action="/settings/apply">
<fieldset><legend>Research configuration</legend>
<label>P-Gap price <input name="p_gap_price" value="{research.p_gap_price}"></label>
<label>Spike multiplier <input name="spike_multiplier" value="{research.spike_multiplier}"></label>
<label>Max SL distance <input name="max_sl_distance" value="{research.max_sl_distance}"></label>
<label>TP R <input name="tp_r" value="{research.tp_r}"></label>
</fieldset>
<fieldset><legend>Operational forward configuration</legend>
<label>Trail distance price <input name="trail_distance_price" value="{forward.trail_distance_price}"></label>
<label>Trail activation price <input name="trail_activation_price" value="{forward.trail_activation_price}"></label>
<label>Volume <input name="volume" value="{forward.volume}"></label>
<label>Pending TTL minutes <input name="pending_ttl_minutes" value="{forward.pending_ttl_minutes}"></label>
<label>Order mode <input name="order_mode" value="{forward.order_mode}"></label>
</fieldset>
<label>Revision <input name="revision" value="{revision}"></label>
<button type="submit">Stage configuration</button>
</form>
<p class="dim">Fingerprint: {fingerprint}</p>
<p><a href="/">Back to dashboard</a></p></body></html>"""


@settings_bp.get("/settings")
def settings() -> Response:
    return Response(_page(), mimetype="text/html")


@settings_bp.post("/settings/apply")
def apply() -> Response:
    try:
        cfg = apply_settings(
            CONFIG_PATH,
            research=ResearchConfig(
                p_gap_price=float(request.form["p_gap_price"]),
                spike_multiplier=float(request.form["spike_multiplier"]),
                max_sl_distance=float(request.form["max_sl_distance"]),
                tp_r=float(request.form["tp_r"]),
            ),
            forward=ForwardConfig(
                trail_distance_price=float(request.form["trail_distance_price"]),
                trail_activation_price=float(request.form["trail_activation_price"]),
                volume=float(request.form["volume"]),
                pending_ttl_minutes=float(request.form["pending_ttl_minutes"]),
                order_mode=request.form["order_mode"].strip(),
            ),
            revision=request.form["revision"].strip(),
        )
        return Response(_page(f"STAGED: {cfg.revision} · fingerprint {cfg.fingerprint}"), mimetype="text/html")
    except (KeyError, ValueError, DashboardConfigError) as exc:
        return Response(_page(f"REJECTED: {exc}"), status=400, mimetype="text/html")


def register_dashboard_settings(app) -> None:
    app.register_blueprint(settings_bp)
