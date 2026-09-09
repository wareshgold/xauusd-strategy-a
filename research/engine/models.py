from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    symbol: str = "XAUUSD"
    timeframe: str = "1m"

    def __post_init__(self) -> None:
        if not (self.low <= self.open <= self.high and self.low <= self.close <= self.high):
            raise ValueError("OHLC invariant violated")
        if self.high < self.low:
            raise ValueError("high must be >= low")


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


@dataclass
class Order:
    order_id: str
    side: Side
    order_type: OrderType
    quantity: float
    created_at: datetime
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    setup_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Fill:
    order_id: str
    timestamp: datetime
    price: float
    quantity: float


@dataclass
class Trade:
    order_id: str
    side: Side
    entry_time: datetime
    entry_price: float
    quantity: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    setup_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def risk_distance(self) -> Optional[float]:
        if self.stop_loss is None:
            return None
        return abs(self.entry_price - self.stop_loss)

    @property
    def r_multiple(self) -> Optional[float]:
        if self.exit_price is None or not self.risk_distance:
            return None
        move = self.exit_price - self.entry_price
        if self.side is Side.SELL:
            move = -move
        return move / self.risk_distance
