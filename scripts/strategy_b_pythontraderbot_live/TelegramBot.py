"""Telegram transport isolated for Strategy B; credentials are read from environment only."""
import os
import requests

token = os.environ.get("STRATEGY_B_TELEGRAM_BOT_TOKEN", "")
chatId = os.environ.get("STRATEGY_B_TELEGRAM_CHAT_ID", "")
proxy_url = os.environ.get("STRATEGY_B_TELEGRAM_PROXY", "").strip() or None

class TeleBot:
    def __init__(self):
        self.url = f"https://api.telegram.org/bot{token}/"
        self.proxies = {"https": proxy_url} if proxy_url else None
        self.chatId = chatId

    def SendMessage(self, message="empty"):
        tagged = f"STRATEGY B | {message}"
        try:
            response = requests.post(
                self.url + "sendMessage",
                data={"chat_id": self.chatId, "text": tagged},
                proxies=self.proxies,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            if result.get("ok"):
                print("Strategy B Telegram message sent.")
                return True
            print(f"Strategy B Telegram API rejected message: {result.get('description', 'unknown error')}")
        except Exception as exc:
            print(f"Strategy B Telegram send failed: {exc}")
        return False
