from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class MetricsContractError(ValueError):
    """Raised when a research-result metrics contract is incomplete or invalid."""


@dataclass(frozen=True)
class ResearchMetrics:
    """Canonical descriptive metric vocabulary for historical research results.

    This contract standardizes measurement fields only. It does not define
    profitability thresholds, acceptance criteria, or canonical strategy rules.
    """

    trades: int
    decisive_trades: int
    wins: int
    losses: int
    ambiguous: int
    win_rate: float
    net_r: float
    profit_factor: float | None
    max_drawdown_r: float
    gross_profit_r: float
    gross_loss_r: float

    def validate(self) -> None:
        integers = {
            "trades": self.trades,
            "decisive_trades": self.decisive_trades,
            "wins": self.wins,
            "losses": self.losses,
            "ambiguous": self.ambiguous,
        }
        if any(not isinstance(v, int) or isinstance(v, bool) or v < 0 for v in integers.values()):
            raise MetricsContractError("trade counts must be non-negative integers")
        if self.decisive_trades != self.wins + self.losses:
            raise MetricsContractError("decisive_trades must equal wins + losses")
        if self.trades != self.decisive_trades + self.ambiguous:
            raise MetricsContractError("trades must equal decisive_trades + ambiguous")
        if self.decisive_trades == 0:
            if self.win_rate != 0.0:
                raise MetricsContractError("win_rate must be zero when there are no decisive trades")
        elif abs(self.win_rate - (self.wins / self.decisive_trades)) > 1e-12:
            raise MetricsContractError("win_rate does not match wins / decisive_trades")
        for name, value in {
            "win_rate": self.win_rate,
            "net_r": self.net_r,
            "max_drawdown_r": self.max_drawdown_r,
            "gross_profit_r": self.gross_profit_r,
            "gross_loss_r": self.gross_loss_r,
        }.items():
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise MetricsContractError(f"{name} must be numeric")
        if not 0.0 <= self.win_rate <= 1.0:
            raise MetricsContractError("win_rate must be between 0 and 1")
        if self.gross_profit_r < 0 or self.gross_loss_r > 0:
            raise MetricsContractError("gross profit/loss signs are invalid")
        if self.max_drawdown_r < 0:
            raise MetricsContractError("max_drawdown_r must be non-negative")
        if self.profit_factor is not None:
            if not isinstance(self.profit_factor, (int, float)) or isinstance(self.profit_factor, bool):
                raise MetricsContractError("profit_factor must be numeric or None")
            if self.profit_factor < 0:
                raise MetricsContractError("profit_factor must be non-negative")

    def as_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "trades": self.trades,
            "decisive_trades": self.decisive_trades,
            "wins": self.wins,
            "losses": self.losses,
            "ambiguous": self.ambiguous,
            "win_rate": self.win_rate,
            "net_r": self.net_r,
            "profit_factor": self.profit_factor,
            "max_drawdown_r": self.max_drawdown_r,
            "gross_profit_r": self.gross_profit_r,
            "gross_loss_r": self.gross_loss_r,
        }
