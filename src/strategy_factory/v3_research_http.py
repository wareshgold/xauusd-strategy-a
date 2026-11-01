from __future__ import annotations

"""Loopback-only HTTP bridge for the V3 interactive research workbench.

The server exposes only research session operations. It never connects to MT5,
writes source datasets, modifies frozen entries, or emits trading decisions.
Dataset roots must be explicitly configured by the operator.
"""

import csv
import hashlib
import json
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .v3_research_api import V3ResearchAPI, V3ResearchAPIError


class V3ResearchHTTPError(ValueError):
    pass


class V3ResearchHTTPApplication:
    def __init__(self, *, data_roots: list[str | Path], api: V3ResearchAPI | None = None) -> None:
        roots = []
        for value in data_roots:
            path = Path(value).expanduser().resolve()
            if path.exists() and path.is_dir() and path not in roots:
                roots.append(path)
        if not roots:
            raise V3ResearchHTTPError("configure at least one existing SP2L_V3_RESEARCH_DATA_ROOTS directory")
        self.data_roots = tuple(roots)
        self.api = api or V3ResearchAPI()

    @classmethod
    def from_environment(cls) -> "V3ResearchHTTPApplication":
        raw = os.getenv("SP2L_V3_RESEARCH_DATA_ROOTS", "")
        roots = [item for item in raw.split(os.pathsep) if item.strip()]
        return cls(data_roots=roots)

    def catalog(self) -> dict[str, Any]:
        found: list[dict[str, Any]] = []
        for root_index, root in enumerate(self.data_roots):
            # Bounded traversal: avoid recursively walking tick archives or the full repo.
            visited = 0
            for directory, subdirs, filenames in os.walk(root):
                current = Path(directory)
                depth = len(current.relative_to(root).parts)
                subdirs[:] = sorted(
                    name for name in subdirs
                    if name not in {".git", ".venv", "__pycache__", "node_modules"}
                ) if depth < 4 else []
                for filename in sorted(filenames):
                    suffix = Path(filename).suffix.lower()
                    if suffix not in {".json", ".csv"}:
                        continue
                    path = current / filename
                    try:
                        stat = path.stat()
                        relative = path.relative_to(root).as_posix()
                    except OSError:
                        continue
                    kind = self._artifact_kind(path)
                    if kind is None:
                        continue
                    item = {
                        "id": f"{root_index}:{relative}",
                        "name": filename,
                        "kind": kind,
                        "relative_path": relative,
                        "size_bytes": stat.st_size,
                        "modified_ns": stat.st_mtime_ns,
                    }
                    if kind == "M1_JSON":
                        try:
                            item.update(self._observed_m1_window(path))
                        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                            item["window_error"] = str(exc)
                    found.append(item)
                    visited += 1
                    if visited >= 500:
                        break
                if visited >= 500:
                    break
        found.sort(key=lambda item: (item["kind"], item["name"].lower(), item["id"]))
        return {
            "research_only": True,
            "roots": [str(root) for root in self.data_roots],
            "items": found,
            "catalog_limit_per_root": 500,
        }

    @staticmethod
    def _observed_m1_window(path: Path) -> dict[str, str]:
        """Read the dataset's own declared JSON window or CSV first/last row times."""
        if path.suffix.lower() == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            window = payload.get("window_utc") if isinstance(payload, dict) else None
            if not isinstance(window, dict) or not window.get("start") or not window.get("end"):
                raise ValueError("M1 JSON has no declared window_utc metadata")
            return {
                "start_utc": str(window["start"]),
                "end_utc": str(window["end"]),
                "window_source": "M1_JSON_DECLARED_WINDOW",
            }
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            first = next(reader, None)
            if first is None:
                raise ValueError("M1 CSV contains no data rows")
            last = first
            for row in reader:
                last = row
        start = datetime.fromtimestamp(int(first["time_epoch_seconds"]), timezone.utc).isoformat()
        end = datetime.fromtimestamp(int(last["time_epoch_seconds"]), timezone.utc).isoformat()
        return {
            "start_utc": start,
            "end_utc": end,
            "window_source": "M1_CSV_OBSERVED_FIRST_LAST_ROWS",
        }

    @staticmethod
    def _artifact_kind(path: Path) -> str | None:
        name = path.name.lower()
        if path.suffix.lower() in {".json", ".csv"} and ("m1" in name or "ohlc" in name):
            return "M1_JSON"
        if path.suffix.lower() == ".csv" and ("entr" in name or "population" in name or "candidate" in name):
            return "FROZEN_ENTRY_CSV"
        return None

    def resolve_artifact(self, artifact_id: str, expected_kind: str) -> Path:
        try:
            root_index_text, relative = artifact_id.split(":", 1)
            root = self.data_roots[int(root_index_text)]
            candidate = (root / Path(relative)).resolve()
        except (ValueError, IndexError, OSError) as exc:
            raise V3ResearchHTTPError("invalid catalog artifact identifier") from exc
        if root not in candidate.parents or not candidate.is_file():
            raise V3ResearchHTTPError("artifact path is outside configured roots or is not a file")
        if self._artifact_kind(candidate) != expected_kind:
            raise V3ResearchHTTPError(f"artifact is not of required type {expected_kind}")
        return candidate

    def create_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {
            "m1_artifact_id", "entry_artifact_id", "symbol",
            "mt5_point", "contract_size", "volume", "engine_revision",
        }
        missing = sorted(required - payload.keys())
        if missing:
            raise V3ResearchHTTPError("missing fields: " + ", ".join(missing))
        m1 = self.resolve_artifact(str(payload["m1_artifact_id"]), "M1_JSON")
        entries = self.resolve_artifact(str(payload["entry_artifact_id"]), "FROZEN_ENTRY_CSV")
        dataset_sha = self._sha256(m1)
        entry_sha = self._sha256(entries)
        observed_window = self._observed_m1_window(m1)
        requested_start = payload.get("start_utc") or observed_window["start_utc"]
        requested_end = payload.get("end_utc") or observed_window["end_utc"]
        config = {
            "m1_artifact": m1,
            "entry_artifact": entries,
            "expected_dataset_sha256": dataset_sha,
            "expected_entry_sha256": entry_sha,
            "expected_symbol": str(payload["symbol"]),
            "expected_start_utc": str(requested_start),
            "expected_end_utc": str(requested_end),
            "mt5_point": float(payload["mt5_point"]),
            "contract_size": float(payload["contract_size"]),
            "volume": float(payload["volume"]),
            "engine_revision": str(payload["engine_revision"]),
        }
        result = self.api.create_session(**config)
        result["artifact_selection"] = {
            "m1_artifact_id": payload["m1_artifact_id"],
            "entry_artifact_id": payload["entry_artifact_id"],
            "dataset_sha256": dataset_sha,
            "entry_sha256": entry_sha,
            "start_utc": str(requested_start),
            "end_utc": str(requested_end),
            "window_source": observed_window["window_source"],
        }
        return result

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def dispatch(self, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        body = body or {}
        try:
            if method == "GET" and path == "/api/health":
                return 200, {"status": "OK", "research_only": True, "canonical": False, "production_decisions": False}
            if method == "GET" and path == "/api/catalog":
                return 200, self.catalog()
            if method == "POST" and path == "/api/sessions":
                return 201, self.create_session(body)
            parts = [unquote(part) for part in path.strip("/").split("/") if part]
            if len(parts) == 3 and parts[0:2] == ["api", "sessions"] and method == "GET":
                return 200, self.api.describe_session(parts[2])
            if len(parts) == 4 and parts[0:2] == ["api", "sessions"] and parts[3] == "evaluate" and method == "POST":
                return 200, self.api.evaluate(
                    parts[2], rr=float(body["rr"]),
                    activation_points=None if body.get("activation_points") is None else float(body["activation_points"]),
                    distance_points=None if body.get("distance_points") is None else float(body["distance_points"]),
                )
            if len(parts) == 4 and parts[0:2] == ["api", "sessions"] and parts[3] == "management" and method == "POST":
                return 200, self.api.evaluate_management(parts[2], body.get("spec", {}))
            if len(parts) == 4 and parts[0:2] == ["api", "sessions"] and parts[3] == "compare" and method == "POST":
                return 200, self.api.compare(parts[2], str(body["left_variant_id"]), str(body["right_variant_id"]))
            return 404, {"error": "route not found"}
        except (V3ResearchAPIError, V3ResearchHTTPError, KeyError, TypeError, ValueError, OSError) as exc:
            return 400, {"error": str(exc), "research_only": True}


def create_handler(app: V3ResearchHTTPApplication, static_html: Path):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, payload: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:
            if self.path == "/":
                try:
                    payload = static_html.read_bytes()
                except OSError:
                    self._send(500, b"Dashboard HTML is unavailable", "text/plain; charset=utf-8")
                    return
                self._send(200, payload, "text/html; charset=utf-8")
                return
            status, result = app.dispatch("GET", self.path)
            self._send(status, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_POST(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 1_000_000:
                    raise V3ResearchHTTPError("request body must be between 1 byte and 1 MB")
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                if not isinstance(payload, dict):
                    raise V3ResearchHTTPError("JSON request body must be an object")
                status, result = app.dispatch("POST", self.path, payload)
            except (ValueError, UnicodeDecodeError, V3ResearchHTTPError) as exc:
                status, result = 400, {"error": str(exc)}
            self._send(status, json.dumps(result, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def log_message(self, fmt: str, *args: Any) -> None:
            return

    return Handler


def serve(*, host: str = "127.0.0.1", port: int = 8791) -> None:
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise V3ResearchHTTPError("research dashboard server must bind to loopback only")
    app = V3ResearchHTTPApplication.from_environment()
    static_html = Path(__file__).resolve().parents[2] / "scripts" / "v3_research_dashboard.html"
    server = ThreadingHTTPServer((host, port), create_handler(app, static_html))
    print(f"V3 Research Dashboard: http://127.0.0.1:{port}/")
    print("Research only · loopback only · production decisions disabled")
    server.serve_forever()
