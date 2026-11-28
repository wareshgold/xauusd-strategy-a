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
) -> dict:
    """Attempt durable event logging and Telegram alert independently."""
    payload = {
        "event": "STARTUP_INITIALIZATION_FAILED",
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
        "⛔ SP2L V3.1 STARTUP FAILED\n"
        f"Reason: {reason}\n"
        "The runner will abort startup; no new orders will be submitted."
    )
    try:
        result = send_alert(message)
        alert_success = bool(getattr(result, "success", False))
        alert_detail = getattr(result, "detail", None)
    except Exception as exc:
        alert_detail = f"{type(exc).__name__}: {exc}"

    try:
        log_event({
            "event": "STARTUP_INITIALIZATION_ALERT",
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
