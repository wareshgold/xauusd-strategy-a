"""Research forward safety gate. Does not define strategy geometry."""


def validate_trade(entry: float, sl: float, tp: float, min_risk: float = 0.01, min_rr: float = 1.0) -> dict:
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr = reward / risk if risk else 0.0
    return {
        "valid": risk >= min_risk and rr >= min_rr,
        "risk": risk,
        "reward": reward,
        "rr": rr,
    }
