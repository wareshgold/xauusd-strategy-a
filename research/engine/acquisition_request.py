"""Strategy-neutral deterministic Twelve Data acquisition request contract."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class AcquisitionRequest:
    symbol: str
    interval: str
    outputsize: int = 5000
    start_date: str | None = None
    end_date: str | None = None
    source_timezone: str | None = None

    def query_params(self, api_key: str) -> dict[str, str]:
        if not api_key:
            raise ValueError("api_key must be supplied outside source control")
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "outputsize": str(self.outputsize),
            "apikey": api_key,
        }
        if self.start_date is not None:
            params["start_date"] = self.start_date
        if self.end_date is not None:
            params["end_date"] = self.end_date
        if self.source_timezone is not None:
            params["timezone"] = self.source_timezone
        return params

    def redacted_query(self) -> str:
        params = self.query_params("REDACTED")
        return urlencode(params)
