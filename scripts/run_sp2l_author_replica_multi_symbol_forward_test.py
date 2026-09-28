def send_signal(candidate: dict, pip_size: float, order_ticket: int | None = None):
    symbol = candidate["symbol"]
    digits = int(mt5.symbol_info(symbol).digits)
    t = display_time_from_mt5(candidate["trigger_time"])
    risk_pips = candidate["risk"] / pip_size if pip_size else 0.0
    icon = "🟢" if candidate["direction"] == "BUY" else "🔴"
    order_line = f"📦 <b>Order</b>   Pending Limit PLACED · #{order_ticket}" if order_ticket else "📦 <b>Order</b>   Pending Limit"

    secondary_entry = candidate.get("secondary_entry_2x")
    secondary_line = (
        f"➕ <b>2X Entry</b> {float(secondary_entry):.{digits}f}  <i>(research)</i>\n"
        if secondary_entry is not None
        else "➕ <b>2X Entry</b> N/A  <i>(execution unresolved)</i>\n"
    )

    text = (
        f"{icon} <b>SP2L — {symbol} {candidate['direction']} — PENDING PLACED</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📌 <b>Entry</b>   {candidate['theoretical_entry']:.{digits}f}\n"
        f"🛑 <b>SL</b>      {candidate['sl']:.{digits}f}\n"
        f"🎯 <b>TP (1R)</b>  {candidate['tp']:.{digits}f}\n"
        f"📏 <b>Risk</b>    {candidate['risk']:.{digits}f}  ({risk_pips:.0f} pip)\n"
        f"{secondary_line}"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{order_line}\n"
        f"⚖️ <b>Volume</b>  {candidate.get('volume', VOLUME):.2f}\n"
        f"🕒 <b>Signal</b>  {t:%H:%M:%S} (UTC+3:30)\n\n"
        f"🆔 <code>AUTHOR_REPLICA_MULTI_{candidate['trigger_time']}_{symbol}_{candidate['direction']}</code>\n"
        f"⚠️ <i>RESEARCH / DEMO ONLY — NOT CANONICAL</i>"
    )
    return gateway.send_telegram_message(text, parse_mode="HTML")
