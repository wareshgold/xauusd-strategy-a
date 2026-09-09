from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .demo_disconnect import EmergencyDisconnect
from .demo_reconciliation import ReconciliationState, ReconciliationResult


class DemoExecutionDecision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


@dataclass
class DemoGateSafety:
    connection: EmergencyDisconnect
    killed: bool = True

    def kill(self) -> None:
        self.killed = True
        self.connection.disconnect()

    def arm(self) -> None:
        if self.killed:
            raise RuntimeError("explicit reset required after kill")
        self.connection.connect()

    def reset_and_arm(self) -> None:
        self.killed = False
        self.connection.connect()

    def decision(self, reconciliation: ReconciliationResult) -> DemoExecutionDecision:
        if self.killed or not self.connection.allow_requests():
            return DemoExecutionDecision.BLOCK
        if reconciliation.state is not ReconciliationState.MATCH:
            return DemoExecutionDecision.BLOCK
        return DemoExecutionDecision.ALLOW
