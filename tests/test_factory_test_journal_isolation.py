from __future__ import annotations

import ast
from pathlib import Path


def _called_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def test_factory_tests_never_use_implicit_persistent_job_ledger():
    """Test helpers must opt into in-memory or temporary journal storage.

    FactoryJobEventLedger() defaults to the runtime JSONL file. A test that
    omits its path can silently contaminate operator evidence, even when the
    test itself is otherwise synthetic. Runtime callers may keep the default;
    tests must pass path=None or an explicit temporary path.
    """
    tests_root = Path(__file__).resolve().parent
    violations: list[str] = []

    for test_path in sorted(tests_root.glob("test_*.py")):
        tree = ast.parse(test_path.read_text(encoding="utf-8"), filename=str(test_path))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and _called_name(node.func) == "FactoryJobEventLedger"
                and not node.args
                and not node.keywords
            ):
                relative_path = test_path.relative_to(tests_root.parent).as_posix()
                violations.append(f"{relative_path}:{node.lineno}")

    assert not violations, (
        "Tests must not use FactoryJobEventLedger()'s implicit runtime journal. "
        "Use FactoryJobEventLedger(path=None) for in-memory fixtures or pass a "
        "tmp_path-backed file. Offending calls: " + ", ".join(violations)
    )
