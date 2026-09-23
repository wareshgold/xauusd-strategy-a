"""MT5 terminal discovery helpers for SP2L forward runtime.

Research infrastructure only. No strategy logic lives here.
"""
from __future__ import annotations

import os
from pathlib import Path


def candidate_paths() -> list[Path]:
    values = []
    env = os.getenv("MT5_TERMINAL_PATH")
    if env:
        values.append(Path(env))

    for root in [
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
    ]:
        if root.exists():
            values.extend(root.glob("MetaTrader*/terminal64.exe"))
            values.extend(root.glob("*/terminal64.exe"))

    return values


def find_mt5_terminal() -> Path | None:
    for path in candidate_paths():
        if path.exists():
            return path
    return None


if __name__ == "__main__":
    terminal = find_mt5_terminal()
    print(str(terminal) if terminal else "MT5_NOT_FOUND")
