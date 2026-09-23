"""Background watchdog for the SP2L multi-symbol forward test runner.

Research/infrastructure only: restarts the runner if it exits and sends
Telegram notifications on DOWN/UP transitions. Never touches strategy
logic, never enables live trading, never places orders itself.

Windows usage (stays alive after the PowerShell window closes):

    python scripts/forward_watchdog.py                # foreground
    start /b python scripts/forward_watchdog.py       # background
    python scripts/forward_watchdog.py --stop         # stop watchdog+runner

Env:
    TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID  (or config/telegram.json)
    FORWARD_WATCHDOG_MAX_RESTARTS   default 20 (then give up + notify)
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from telegram_client import send_telegram_message  # noqa: E402

RUNNER = ROOT / "scripts" / "run_sp2l_author_replica_multi_symbol_forward_test.py"
LOG = ROOT / "artifacts" / "forward-test" / "runner_stdout.log"
WATCHDOG_PID = ROOT / "runtime" / "forward_watchdog.pid"
MAX_RESTARTS = int(os.getenv("FORWARD_WATCHDOG_MAX_RESTARTS", "20"))
RESTART_DELAY_SECONDS = 5


def notify(text: str) -> None:
    result = send_telegram_message(text)
    print(f"[watchdog] telegram: {result.detail}")


def spawn_runner() -> subprocess.Popen:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    log_handle = LOG.open("ab")
    return subprocess.Popen(
        [sys.executable, str(RUNNER)],
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        cwd=str(ROOT),
    )


def stop_everything() -> None:
    WATCHDOG_PID.parent.mkdir(parents=True, exist_ok=True)
    if WATCHDOG_PID.exists():
        try:
            pid = int(WATCHDOG_PID.read_text(encoding="utf-8").strip() or 0)
            if pid and pid != os.getpid():
                os.kill(pid, 9)
                print(f"[watchdog] stopped watchdog pid {pid}")
        except (OSError, ValueError):
            pass
        WATCHDOG_PID.unlink(missing_ok=True)


def main() -> None:
    if "--stop" in sys.argv:
        stop_everything()
        return

    WATCHDOG_PID.parent.mkdir(parents=True, exist_ok=True)
    WATCHDOG_PID.write_text(str(os.getpid()), encoding="utf-8")

    notify(
        "🟢 SP2L Forward watchdog started\n"
        f"Runner: {RUNNER.name}\n"
        "⚠️ RESEARCH / DEMO ONLY"
    )

    restarts = 0
    while restarts < MAX_RESTARTS:
        proc = spawn_runner()
        started = datetime.now(timezone.utc).isoformat()
        code = proc.wait()
        if code == 0 and os.getenv("FORWARD_WATCHDOG_STOP_ON_CLEAN_EXIT") == "1":
            break
        notify(
            "🔴 SP2L Forward runner DOWN\n"
            f"exit code: {code}\n"
            f"started: {started}\n"
            f"restarts so far: {restarts}/{MAX_RESTARTS}"
        )
        restarts += 1
        time.sleep(RESTART_DELAY_SECONDS)
        notify("🟠 SP2L Forward runner restarting…")

    notify(
        "⛔ SP2L Forward watchdog giving up\n"
        f"max restarts reached ({MAX_RESTARTS}). Check terminal/MT5."
    )
    WATCHDOG_PID.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
