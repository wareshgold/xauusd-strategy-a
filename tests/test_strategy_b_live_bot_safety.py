"""Static safety checks for the isolated Strategy B execution replica."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
BOT = ROOT / "scripts" / "strategy_b_pythontraderbot_live" / "SP2L_Advanced_Bot_Optimized.py"
META = ROOT / "scripts" / "strategy_b_pythontraderbot_live" / "Meta.py"
TELEGRAM = ROOT / "scripts" / "strategy_b_pythontraderbot_live" / "TelegramBot.py"

def test_live_bot_has_opt_in_terminal_server_and_demo_account_gates():
    source = BOT.read_text(encoding="utf-8")
    assert 'STRATEGY_B_LIVE_TRADING_ENABLE' in source
    assert 'STRATEGY_B_ALLOW_DEMO_EXECUTION' in source
    assert 'STRATEGY_B_MT5_TERMINAL_PATH' in source
    assert 'mt5.initialize(path=TERMINAL_PATH, timeout=10000)' in source
    assert 'mt5.ACCOUNT_TRADE_MODE_DEMO' in source
    assert 'EXPECTED_SERVER' in source
    assert 'if not mt5.initialize()' not in source
    assert 'strategy_b_pythontraderbot_live.lock' in source
    assert 'STRATEGY_B lock exists' in source
    assert 'FORWARD TEST STARTED' in source
    assert 'BLOCKED: Strategy B Telegram startup check failed' in source

def test_strategy_b_uses_explicit_broker_symbol_and_source_settings():
    source = BOT.read_text(encoding="utf-8")
    assert 'EXPECTED_SYMBOL = os.environ.get("STRATEGY_B_SYMBOL", "XAUUSD.ecn")' in source
    assert 'NUMBER_OF_DATA = 500' in source
    assert 'SPIKE_CANDLE_SIZE = 1.5' in source
    assert 'PGAP_POINTS = 100' in source
    assert 'MAX_SL_DISTANCE_POINTS = 1000' in source
    assert 'TP_R = 0.9' in source
    assert 'MAGIC = 8' in source and 'SECOND_ENTRY_MAGIC = 9' in source
    assert 'USE_SECOND_ENTRY = False' in source

def test_broker_symbol_is_not_auto_selected_and_order_comment_is_strategy_b():
    source = BOT.read_text(encoding="utf-8")
    meta = META.read_text(encoding="utf-8")
    assert 'mt5.symbol_select(' not in source
    assert 'comment="Strategy B PythonTraderBot"' in meta
    assert 'comment=" No specific comment"' not in meta
    assert 'BLOCKED: existing Strategy B magic 8/9 exposure detected' in source

def test_telegram_is_environment_configured_and_tags_all_messages():
    source = TELEGRAM.read_text(encoding="utf-8")
    bot = BOT.read_text(encoding="utf-8")
    assert 'STRATEGY_B_TELEGRAM_BOT_TOKEN' in source
    assert 'STRATEGY B | {message}' in source
    assert 'Meta.teleBotMessage = True' in bot

def test_all_python_files_parse_without_running_the_bot():
    for path in (BOT, META, TELEGRAM):
        ast.parse(path.read_text(encoding="utf-8"))
