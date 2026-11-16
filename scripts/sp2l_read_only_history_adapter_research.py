"""Injected read-only MT5 history adapter contract for offline research.

This module has no MetaTrader5 import and never initializes or connects to a
terminal. It accepts an injected provider solely so deterministic fakes can
exercise the documented call shape. Passing a real MT5 module/provider is
outside this contract and requires a separately authorized compatibility gate.

The adapter preserves returned records as opaque objects. It does not reconcile
orders/deals/positions, infer fill semantics, establish history completeness,
or make execution decisions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol


class HistoryProvider(Protocol):
    """Minimal injected surface matching the documented Python call shape."""

    def history_orders_get(self, *, position: int) -> Any:
        ...

    def history_deals_get(self, *, position: int) -> Any:
        ...

    def last_error(self) -> Any:
        ...


class HistoryQueryKind(str, Enum):
    ORDERS = "orders"
    DEALS = "deals"


class HistoryQueryStatus(str, Enum):
    NON_EMPTY = "non_empty"
    EMPTY = "empty"
    ERROR = "error"


class HistoryFailureCode(str, Enum):
    API_RETURNED_NONE = "api_returned_none"
    PROVIDER_EXCEPTION = "provider_exception"
    INVALID_RESULT_TYPE = "invalid_result_type"


@dataclass(frozen=True)
class HistoryQueryResult:
    """One query outcome; raw rows and API error payload remain unmodified."""

    query_kind: HistoryQueryKind
    position_identifier: int
    status: HistoryQueryStatus
    records: tuple[Any, ...] = ()
    failure_code: HistoryFailureCode | None = None
    api_last_error: Any = None
    diagnostic_exception_type: str | None = None
    last_error_exception_type: str | None = None


class ReadOnlyHistoryAdapterResearch:
    """Small injected-provider seam; no direct MT5 dependency or side effects."""

    def __init__(self, provider: HistoryProvider) -> None:
        self._provider = provider

    @staticmethod
    def _validate_position_identifier(position_identifier: int) -> None:
        # bool is an int subclass but is not a valid identifier argument.
        if isinstance(position_identifier, bool) or not isinstance(
            position_identifier, int
        ):
            raise TypeError("position_identifier must be an integer")
        if position_identifier <= 0:
            raise ValueError("position_identifier must be positive")

    def history_orders(
        self, *, position_identifier: int
    ) -> HistoryQueryResult:
        return self._query(
            kind=HistoryQueryKind.ORDERS,
            method_name="history_orders_get",
            position_identifier=position_identifier,
        )

    def history_deals(
        self, *, position_identifier: int
    ) -> HistoryQueryResult:
        return self._query(
            kind=HistoryQueryKind.DEALS,
            method_name="history_deals_get",
            position_identifier=position_identifier,
        )

    def _query(
        self,
        *,
        kind: HistoryQueryKind,
        method_name: str,
        position_identifier: int,
    ) -> HistoryQueryResult:
        self._validate_position_identifier(position_identifier)
        method = getattr(self._provider, method_name)

        try:
            raw = method(position=position_identifier)
        except Exception as exc:
            return HistoryQueryResult(
                query_kind=kind,
                position_identifier=position_identifier,
                status=HistoryQueryStatus.ERROR,
                failure_code=HistoryFailureCode.PROVIDER_EXCEPTION,
                api_last_error=self._read_last_error()[0],
                diagnostic_exception_type=type(exc).__name__,
                last_error_exception_type=self._read_last_error()[1],
            )

        if raw is None:
            return HistoryQueryResult(
                query_kind=kind,
                position_identifier=position_identifier,
                status=HistoryQueryStatus.ERROR,
                failure_code=HistoryFailureCode.API_RETURNED_NONE,
                api_last_error=self._read_last_error()[0],
                last_error_exception_type=self._read_last_error()[1],
            )

        # The documented Python API returns a tuple (including an empty tuple).
        # Do not silently coerce lists, generators, or arbitrary iterables.
        if not isinstance(raw, tuple):
            return HistoryQueryResult(
                query_kind=kind,
                position_identifier=position_identifier,
                status=HistoryQueryStatus.ERROR,
                failure_code=HistoryFailureCode.INVALID_RESULT_TYPE,
                diagnostic_exception_type=type(raw).__name__,
            )

        return HistoryQueryResult(
            query_kind=kind,
            position_identifier=position_identifier,
            status=(
                HistoryQueryStatus.NON_EMPTY
                if raw
                else HistoryQueryStatus.EMPTY
            ),
            records=raw,
        )

    def _read_last_error(self) -> tuple[Any, str | None]:
        try:
            return self._provider.last_error(), None
        except Exception as exc:
            # Keep API error payload empty; report getter failure separately.
            return None, type(exc).__name__
