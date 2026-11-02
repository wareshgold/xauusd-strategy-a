"""Tests for Telegram credential source precedence; never sends messages."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from telegram_client import read_telegram_env


class TelegramEnvironmentTests(unittest.TestCase):
    @patch("telegram_client.read_telegram_config", return_value=("file-token", "file-chat"))
    def test_complete_process_environment_pair_takes_precedence(self, read_config):
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "env-token",
            "TELEGRAM_CHAT_ID": "env-chat",
        }, clear=True):
            self.assertEqual(read_telegram_env(), ("env-token", "env-chat"))
        read_config.assert_not_called()

    @patch("telegram_client.read_telegram_config", return_value=("file-token", "file-chat"))
    def test_partial_process_environment_does_not_mix_with_file(self, read_config):
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "env-token",
        }, clear=True):
            self.assertEqual(read_telegram_env(), ("env-token", None))
        read_config.assert_not_called()

    @patch("telegram_client.read_telegram_config", return_value=("file-token", "file-chat"))
    def test_empty_process_environment_falls_back_to_local_config(self, read_config):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(read_telegram_env(), ("file-token", "file-chat"))
        read_config.assert_called_once_with()

    @patch("telegram_client.read_telegram_config")
    def test_explicit_mapping_is_isolated_from_process_environment(self, read_config):
        with patch.dict(os.environ, {
            "TELEGRAM_BOT_TOKEN": "process-token",
            "TELEGRAM_CHAT_ID": "process-chat",
        }, clear=True):
            self.assertEqual(read_telegram_env({}), (None, None))
        read_config.assert_not_called()


if __name__ == "__main__":
    unittest.main()
