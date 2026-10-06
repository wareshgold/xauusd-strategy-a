from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


class DashboardConfigError(ValueError):
    """Raised when dashboard-managed configuration is invalid."""


@dataclass(frozen=True)
class ResearchConfig:
    p_gap_price: float = 1.0
    spike_multiplier: float = 1.5
    max_sl_distance: float = 10.0
    tp_r: float = 2.0


@dataclass(frozen=True)
class ForwardConfig:
    trail_distance_price: float = 0.02
    trail_activation_price: float = 0.10
    volume: float = 0.01
    pending_ttl_minutes: float = 30.0
    order_mode: str = "PENDING_LIMIT_RESEARCH"


@dataclass(frozen=True)
class DashboardConfig:
    revision: str
    research: ResearchConfig
    forward: ForwardConfig
    fingerprint: str

    def _payload(self) -> dict[str, object]:
        return {
            "revision": self.revision,
            "research": asdict(self.research),
            "forward": asdict(self.forward),
        }

    def validate(self) -> None:
        if not self.revision:
            raise DashboardConfigError("configuration revision is required")
        r = self.research
        f = self.forward
        if r.p_gap_price < 0 or r.spike_multiplier <= 0 or r.max_sl_distance <= 0 or r.tp_r <= 0:
            raise DashboardConfigError("research configuration contains invalid numeric values")
        if f.trail_distance_price <= 0 or f.trail_activation_price < 0 or f.volume <= 0 or f.pending_ttl_minutes < 0:
            raise DashboardConfigError("forward configuration contains invalid numeric values")
        if not f.order_mode:
            raise DashboardConfigError("forward order_mode is required")
        expected = _fingerprint(self._payload())
        if self.fingerprint != expected:
            raise DashboardConfigError("dashboard configuration fingerprint mismatch")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {**self._payload(), "fingerprint": self.fingerprint}

    @property
    def apply_mode(self) -> str:
        return "STAGED_FORWARD_CONFIG"


def _fingerprint(payload: dict[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def build_config(
    *,
    revision: str,
    research: ResearchConfig,
    forward: ForwardConfig,
) -> DashboardConfig:
    draft = DashboardConfig(revision, research, forward, "")
    return DashboardConfig(
        revision=revision,
        research=research,
        forward=forward,
        fingerprint=_fingerprint(draft._payload()),
    )


def default_config() -> DashboardConfig:
    return build_config(
        revision="DASHBOARD-CONFIG-1",
        research=ResearchConfig(),
        forward=ForwardConfig(),
    )


def load_config(path: Path) -> DashboardConfig:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        cfg = DashboardConfig(
            revision=str(payload["revision"]),
            research=ResearchConfig(**payload["research"]),
            forward=ForwardConfig(**payload["forward"]),
            fingerprint=str(payload["fingerprint"]),
        )
        cfg.validate()
        return cfg
    except DashboardConfigError:
        raise
    except Exception as exc:
        raise DashboardConfigError(f"cannot load dashboard configuration: {exc}") from exc


def save_config(path: Path, config: DashboardConfig) -> DashboardConfig:
    config.validate()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(config.as_dict(), indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile = None, None
    try:
        with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, prefix=f".{path.name}.", suffix=".tmp") as tmp:
            tmp.write(payload)
            temp_name = tmp.name
        os.replace(temp_name, path)
    except Exception as exc:
        if temp_name:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
        raise DashboardConfigError(f"cannot save dashboard configuration: {exc}") from exc
    return config


def apply_settings(
    path: Path,
    *,
    research: ResearchConfig,
    forward: ForwardConfig,
    revision: str,
) -> DashboardConfig:
    """Persist a validated staged configuration.

    This intentionally does not mutate the running MT5 process or place orders.
    The runner must explicitly consume a new profile/restart it before settings
    affect execution.
    """
    return save_config(path, build_config(revision=revision, research=research, forward=forward))
