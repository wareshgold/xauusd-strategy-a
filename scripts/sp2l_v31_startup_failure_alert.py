"""Best-effort notification for startup failures before the V3.1 recovery hook.

Notification and event logging are independent best-effort side effects. The
caller remains responsible for aborting startup; this helper never authorizes
continuation when either side effect fails.
"""
from __future__ import annotations


def report_startup_failure(
    *,
    reason: str,
    details: dict,
    version: str,
    send_alert,
    log_event,
    event_name: str = "STARTUP_INITIALIZATION_FAILED",
    alert_heading: str = "STARTUP FAILED",
    alert_instruction: str = "The runner will abort startup; no new orders will be submitted.",
) -> dict:
    """Attempt durable event logging and Telegram alert independently."""
    payload = {
        "event": str(event_name),
        "version": str(version),
        "reason": str(reason),
        "details": dict(details or {}),
        "canonical": False,
    }
    logged = False
    try:
        log_event(payload)
        logged = True
    except Exception:
        # Logging failure must not suppress the independent operator alert.
        pass

    alert_success = False
    alert_detail = None
    message = (
        f"⛔ SP2L V3.1 {alert_heading}\n"
        f"Reason: {reason}\n"
        f"{alert_instruction}"
    )
    try:
        result = send_alert(message)
        alert_success = bool(getattr(result, "success", False))
        alert_detail = getattr(result, "detail", None)
    except Exception as exc:
        alert_detail = f"{type(exc).__name__}: {exc}"

    try:
        log_event({
            "event": f"{event_name}_ALERT",
            "version": str(version),
            "success": alert_success,
            "detail": alert_detail,
            "canonical": False,
        })
    except Exception:
        pass

    return {
        "logged": logged,
        "alerted": alert_success,
        "alert_detail": alert_detail,
    }
