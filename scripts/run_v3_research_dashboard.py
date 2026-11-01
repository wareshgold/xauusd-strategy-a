from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from strategy_factory.v3_research_http import serve


if __name__ == "__main__":
    serve(
        host="127.0.0.1",
        port=int(__import__("os").getenv("SP2L_V3_RESEARCH_PORT", "8791")),
    )
