"""Immutable dataset manifest primitives for reproducible research."""

from dataclasses import dataclass, asdict
import hashlib
import json
from datetime import timezone
from typing import Iterable

from .models import Candle


@dataclass(frozen=True)
class DatasetManifest:
    provider: str
    symbol: str
    timeframe: str
    timezone: str
    first_timestamp: str
    last_timestamp: str
    row_count: int
    sha256: str
    source_version: str = "unknown"

    def canonical_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))


def build_manifest(candles: Iterable[Candle], *, provider: str, symbol: str,
                   timeframe: str, source_version: str = "unknown") -> DatasetManifest:
    rows = sorted(candles, key=lambda x: x.timestamp)
    if not rows:
        raise ValueError("dataset must contain at least one candle")
    payload = "\n".join(
        f"{c.timestamp.astimezone(timezone.utc).isoformat()}|{c.open}|{c.high}|{c.low}|{c.close}"
        for c in rows
    ).encode()
    return DatasetManifest(
        provider=provider, symbol=symbol, timeframe=timeframe, timezone="UTC",
        first_timestamp=rows[0].timestamp.astimezone(timezone.utc).isoformat(),
        last_timestamp=rows[-1].timestamp.astimezone(timezone.utc).isoformat(),
        row_count=len(rows), sha256=hashlib.sha256(payload).hexdigest(),
        source_version=source_version,
    )
