from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConnectionState(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"


@dataclass
class EmergencyDisconnect:
    state: ConnectionState = ConnectionState.DISCONNECTED

    def connect(self) -> None:
        self.state = ConnectionState.CONNECTED

    def disconnect(self) -> None:
        self.state = ConnectionState.DISCONNECTED

    def allow_requests(self) -> bool:
        return self.state is ConnectionState.CONNECTED
