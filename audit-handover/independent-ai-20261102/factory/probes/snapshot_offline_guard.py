"""Audit-only pytest guard for synthetic snapshot tests; no external access."""
import importlib.util
import os
from pathlib import Path
import sys

for key in list(os.environ):
    if any(word in key.upper() for word in ("TOKEN", "SECRET", "PASSWORD", "TELEGRAM", "ACCOUNT", "MT5_LOGIN")):
        os.environ.pop(key, None)
os.environ["LIVE_TRADING_ENABLE"] = "false"
os.environ["ALLOW_REAL_EXECUTION"] = "false"
if importlib.util.find_spec("MetaTrader5") is not None:
    raise RuntimeError("Synthetic environment must not contain real MetaTrader5")

# Do not open any existing research/holdout data, runtime journals, or artifacts.
# Tests use only fresh temporary fixtures. Repository source/docs remain readable.
root = Path("/agent/workspace/sp2l-factory-snapshot-fix")
protected = tuple(str(root / name) + os.sep for name in ("data", "artifacts", "runtime"))

def enforce_offline(event, args):
    if event in ("socket.connect", "socket.getaddrinfo"):
        raise RuntimeError("Synthetic test blocked network access")
    if event == "import" and args[0] == "MetaTrader5":
        raise RuntimeError("Synthetic test blocked MT5 import")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = os.path.abspath(os.fsdecode(args[0]))
        if path.startswith(protected):
            raise RuntimeError("Synthetic test blocked existing dataset/artifact/runtime access")

sys.addaudithook(enforce_offline)
