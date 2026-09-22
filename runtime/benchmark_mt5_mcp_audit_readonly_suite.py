import asyncio
import json
import os
from datetime import datetime, timedelta, timezone

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_URL = "http://127.0.0.1:22346/mcp"
SYMBOL = "XAUUSD.ecn"


def result_text(result):
    if result is None:
        return ""
    parts = []
    for item in getattr(result, "content", []) or []:
        value = getattr(item, "text", None)
        if value:
            parts.append(value)
    return "\n".join(parts)


def summary(label, result):
    text = result_text(result) or str(result)
    print(f"=== {label} ===")
    print(text[:12000])
    print()


async def call(session, name, args):
    started = datetime.now(timezone.utc)
    try:
        result = await session.call_tool(name, args)
        elapsed = (datetime.now(timezone.utc) - started).total_seconds() * 1000
        print(f"{name}: OK ({elapsed:.2f} ms)")
        return result
    except Exception as exc:
        elapsed = (datetime.now(timezone.utc) - started).total_seconds() * 1000
        print(f"{name}: ERROR ({elapsed:.2f} ms): {exc}")
        return None


def parse_local_time(result):
    raw = result_text(result)
    try:
        data = json.loads(raw)
        return datetime.fromisoformat(data["local_time"])
    except Exception:
        return None


async def main():
    api_key = os.environ["MT5_MCP_API_KEY"]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "MCP-Protocol-Version": "2025-06-18",
    }

    async with httpx.AsyncClient(headers=headers, timeout=20.0) as http_client:
        async with streamable_http_client(
            MCP_URL, http_client=http_client
        ) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                time_result = await call(session, "get_time_information", {})
                summary("TIME INFORMATION", time_result)

                local_now = parse_local_time(time_result)
                if local_now is None:
                    raise RuntimeError(
                        "Could not parse terminal local_time from MCP; "
                        "refusing to invent a journal time window."
                    )

                # Journal APIs explicitly require terminal-host local time.
                local_from = (local_now - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                )
                local_to = local_now.isoformat(timespec="seconds")

                # Trading history APIs accept ISO datetimes. Use the MCP UTC
                # clock from the same response rather than the Python host clock.
                try:
                    time_data = json.loads(result_text(time_result))
                    utc_now = datetime.fromisoformat(
                        time_data["utc_time"].replace("Z", "+00:00")
                    )
                except Exception as exc:
                    raise RuntimeError(
                        "Could not parse MCP utc_time; refusing to invent "
                        "a history window."
                    ) from exc

                utc_from = (utc_now - timedelta(hours=1)).isoformat(
                    timespec="seconds"
                ).replace("+00:00", "Z")
                utc_to = utc_now.isoformat(timespec="seconds").replace(
                    "+00:00", "Z"
                )

                print(
                    f"\nWINDOWS\n"
                    f"Journal local terminal time: {local_from} -> {local_to}\n"
                    f"History ISO time: {utc_from} -> {utc_to}\n"
                )

                journal_args = {
                    "datetime_from": local_from,
                    "datetime_to": local_to,
                    "limit": 100,
                }
                expert_args = {
                    "datetime_from": local_from,
                    "datetime_to": local_to,
                    "limit": 100,
                }
                positions_args = {
                    "datetime_from": utc_from,
                    "datetime_to": utc_to,
                    "symbol": SYMBOL,
                    "limit": 1000,
                }
                orders_args = {
                    "datetime_from": utc_from,
                    "datetime_to": utc_to,
                    "symbol": SYMBOL,
                    "include_orders": True,
                    "include_orders_canceled": True,
                    "include_deals": True,
                    "limit": 1000,
                }

                terminal_journal = await call(
                    session, "get_terminal_journal", journal_args
                )
                summary("TERMINAL JOURNAL (LAST HOUR)", terminal_journal)

                expert_journal = await call(
                    session, "get_expert_journal", expert_args
                )
                summary("EXPERT JOURNAL (LAST HOUR)", expert_journal)

                positions = await call(
                    session, "get_trading_history_positions", positions_args
                )
                summary(
                    f"TRADE HISTORY POSITIONS ({SYMBOL}, LAST HOUR)",
                    positions,
                )

                orders = await call(
                    session, "get_trading_history_orders", orders_args
                )
                summary(
                    f"TRADE HISTORY ORDERS/DEALS ({SYMBOL}, LAST HOUR)",
                    orders,
                )

                print("=== AUDIT SUITE COMPLETE ===")
                print("Read-only tools only; no trading tools were called.")


if __name__ == "__main__":
    asyncio.run(main())
