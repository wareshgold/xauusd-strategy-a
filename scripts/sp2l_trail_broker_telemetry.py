"""Best-effort, read-only broker evidence for V3.1 trailing SL requests.

This module observes request/response/readback state only. It never decides
whether a request should be sent, retried, accepted, or rejected.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _last_error(mt5_api) -> str | None:
    try:
        return str(mt5_api.last_error())
    except Exception as exc:  # telemetry must not affect order management
        return f"last_error_unavailable:{type(exc).__name__}:{exc}"


def _safe_log(log_event, event: dict) -> bool:
    """Best-effort event write; telemetry exceptions never escape to caller."""
    try:
        log_event(event)
        return True
    except Exception:
        return False


def execute_and_verify_trailing_request(mt5_api, log_event, request: dict, context: dict):
    """Send one already-approved SLTP request and capture a ticket readback.

    The caller retains full control of eligibility and retry decisions. This
    function invokes order_send exactly once, then performs a read-only
    positions_get(ticket=...) observation. It does not retry.
    """
    common = dict(context)
    common["request_timestamp_utc"] = _utc_now()
    trail_cycle_id = str(common["trail_cycle_id"])
    trail_attempt_id = str(common["trail_attempt_id"])
    ticket = int(common["position_ticket"])
    requested_sl = float(request["sl"])
    tick_size = float(common.get("tick_size") or 0.0)
    digits = int(common.get("digits") or 0)
    tolerance = max(tick_size * 0.5, (10.0 ** (-digits)) * 0.5, 1e-9)

    write_failures = 0
    if not _safe_log(log_event, {
        "event": "TRAIL_REQUEST",
        **common,
        "request": dict(request),
        "canonical": False,
    }):
        write_failures += 1

    # Preserve the existing order_send call semantics: exceptions still
    # propagate exactly as they did before this telemetry wrapper.
    response = mt5_api.order_send(request)
    retcode = getattr(response, "retcode", None) if response is not None else None
    try:
        retcode = int(retcode) if retcode is not None else None
    except (TypeError, ValueError, OverflowError):
        retcode = None
    api_success = bool(
        response is not None
        and retcode == getattr(mt5_api, "TRADE_RETCODE_DONE", 10009)
    )
    response_event = {
        "event": "TRAIL_RESPONSE",
        "trail_cycle_id": trail_cycle_id,
        "trail_attempt_id": trail_attempt_id,
        "position_ticket": ticket,
        "response_timestamp_utc": _utc_now(),
        "api_returned": response is not None,
        "api_success": api_success,
        "retcode": retcode,
        "retcode_external": getattr(response, "retcode_external", None) if response is not None else None,
        "request_id": getattr(response, "request_id", None) if response is not None else None,
        "order": getattr(response, "order", None) if response is not None else None,
        "deal": getattr(response, "deal", None) if response is not None else None,
        "volume": getattr(response, "volume", None) if response is not None else None,
        "price": getattr(response, "price", None) if response is not None else None,
        "bid": getattr(response, "bid", None) if response is not None else None,
        "ask": getattr(response, "ask", None) if response is not None else None,
        "comment": str(getattr(response, "comment", "")) if response is not None else None,
        "canonical": False,
    }
    if response is None:
        response_event["last_error"] = _last_error(mt5_api)
    if not _safe_log(log_event, response_event):
        write_failures += 1

    query_error = None
    try:
        positions = mt5_api.positions_get(ticket=ticket)
    except Exception as exc:
        positions = None
        query_error = f"{type(exc).__name__}:{exc}"

    observed = None
    observed_sl = None
    observed_tp = None
    observed_identifier = None
    try:
        if positions is None:
            query_outcome = "QUERY_FAILED"
            query_error = query_error or _last_error(mt5_api)
        else:
            matches = [
                position for position in positions
                if int(getattr(position, "ticket", 0) or 0) == ticket
            ]
            if not matches:
                query_outcome = "POSITION_NOT_FOUND"
            else:
                query_outcome = "OK"
                observed = matches[0]
                observed_sl = float(getattr(observed, "sl", 0.0) or 0.0)
                observed_tp = float(getattr(observed, "tp", 0.0) or 0.0)
                observed_identifier = int(getattr(observed, "identifier", 0) or 0) or None
    except Exception as exc:
        # Malformed/unexpected readback data is telemetry failure, never a
        # reason to interrupt the runner's already-completed SLTP operation.
        query_outcome = "QUERY_FAILED"
        query_error = f"readback_parse_failed:{type(exc).__name__}:{exc}"
        observed = None
        observed_sl = None
        observed_tp = None
    observation_event = {
        "event": "TRAIL_BROKER_OBSERVATION",
        "trail_cycle_id": trail_cycle_id,
        "trail_attempt_id": trail_attempt_id,
        "position_ticket": ticket,
        "observation_timestamp_utc": _utc_now(),
        "query_outcome": query_outcome,
        "observed_sl": observed_sl,
        "observed_tp": observed_tp,
        "position_identifier": observed_identifier,
        "canonical": False,
    }
    if query_error is not None:
        observation_event["last_error"] = query_error
    if not _safe_log(log_event, observation_event):
        write_failures += 1

    if query_outcome == "QUERY_FAILED":
        verification_status = "OBSERVATION_FAILED"
    elif query_outcome == "POSITION_NOT_FOUND":
        verification_status = "POSITION_NOT_FOUND"
    elif math.isclose(observed_sl, requested_sl, rel_tol=0.0, abs_tol=tolerance):
        verification_status = "CONFIRMED_MATCH"
    else:
        verification_status = "OBSERVED_MISMATCH"

    if not _safe_log(log_event, {
        "event": "TRAIL_VERIFICATION",
        "trail_cycle_id": trail_cycle_id,
        "trail_attempt_id": trail_attempt_id,
        "position_ticket": ticket,
        "verification_timestamp_utc": _utc_now(),
        "requested_sl": requested_sl,
        "observed_sl": observed_sl,
        "comparison_tolerance": tolerance,
        "query_outcome": query_outcome,
        "verification_status": verification_status,
        "api_success": api_success,
        "canonical": False,
    }):
        write_failures += 1

    return response, {
        "trail_cycle_id": trail_cycle_id,
        "trail_attempt_id": trail_attempt_id,
        "api_success": api_success,
        "retcode": retcode,
        "verification_status": verification_status,
        "observed_sl": observed_sl,
        "query_outcome": query_outcome,
        "telemetry_write_failures": write_failures,
    }
