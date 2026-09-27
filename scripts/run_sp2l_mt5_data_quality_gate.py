"""Apply the deterministic SP2L MT5 data-quality gate to a matrix artifact."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sp2l_mt5_data_quality_gate import evaluate_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    source = Path(args.artifact)
    data = json.loads(source.read_text(encoding="utf-8"))
    result = evaluate_artifact(data)
    result["source_artifact"] = str(source)
    result["generated_utc"] = datetime.now(timezone.utc).isoformat()

    output = Path(args.output) if args.output else source.with_name(
        source.stem + "_DATA_QUALITY_GATE.json"
    )
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "cases": result["cases"],
        "pass_cases": result["pass_cases"],
        "unresolved_cases": result["unresolved_cases"],
        "output": str(output),
        "canonical": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
