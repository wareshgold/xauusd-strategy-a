"""Single forward-test Telegram message formatter."""


def format_signal(symbol: str, direction: str, entry: float, sl: float, tp: float, rr: float) -> str:
    return (
        f"SP2L {symbol} {direction}\n"
        f"Entry: {entry:.2f}\n"
        f"SL: {sl:.2f}\n"
        f"TP: {tp:.2f}\n"
        f"RR: {rr:.2f}"
    )
