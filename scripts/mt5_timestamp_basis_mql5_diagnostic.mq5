//+------------------------------------------------------------------+
//| mt5_timestamp_basis_mql5_diagnostic.mq5                           |
//| Source-resolution diagnostic: compare MT5 server/time functions  |
//| with raw tick/bar timestamps. No data shifting or repair.        |
//+------------------------------------------------------------------+
#property strict
#property script_show_inputs

input string InpSymbol = "XAUUSD.ecn";
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_M1;

string Ts(datetime t)
{
   return TimeToString(t, TIME_DATE|TIME_SECONDS);
}

void PrintTimePair(string name, datetime t)
{
   Print(name, " epoch=", (long)t, " text=", Ts(t));
}

void OnStart()
{
   string symbol = InpSymbol;
   if(!SymbolSelect(symbol, true))
   {
      Print("symbol_select_failed=true error=", GetLastError());
      return;
   }

   MqlTick tick;
   bool tick_ok = SymbolInfoTick(symbol, tick);

   datetime t_time_current = TimeCurrent();
   datetime t_time_trade_server = TimeTradeServer();
   datetime t_time_local = TimeLocal();
   datetime t_time_gmt = TimeGMT();

   Print("=== MT5 TIMESTAMP BASIS DIAGNOSTIC ===");
   Print("terminal=", TerminalInfoString(TERMINAL_NAME));
   Print("company=", TerminalInfoString(TERMINAL_COMPANY));
   Print("server=", AccountInfoString(ACCOUNT_SERVER));
   Print("symbol=", symbol);
   PrintTimePair("TimeCurrent", t_time_current);
   PrintTimePair("TimeTradeServer", t_time_trade_server);
   PrintTimePair("TimeLocal", t_time_local);
   PrintTimePair("TimeGMT", t_time_gmt);
   Print("TimeTradeServer_minus_TimeGMT_seconds=", (long)(t_time_trade_server-t_time_gmt));
   Print("TimeCurrent_minus_TimeGMT_seconds=", (long)(t_time_current-t_time_gmt));
   Print("TimeLocal_minus_TimeGMT_seconds=", (long)(t_time_local-t_time_gmt));

   if(tick_ok)
   {
      Print("tick_ok=true");
      Print("tick.time_epoch=", (long)tick.time);
      Print("tick.time_text=", Ts(tick.time));
      Print("tick.time_msc=", (long)tick.time_msc);
      Print("tick_time_minus_TimeGMT_seconds=", (long)(tick.time-t_time_gmt));
      Print("tick_time_minus_TimeTradeServer_seconds=", (long)(tick.time-t_time_trade_server));
      Print("tick_time_minus_TimeCurrent_seconds=", (long)(tick.time-t_time_current));
   }
   else
      Print("tick_ok=false error=", GetLastError());

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(symbol, InpTimeframe, 0, 3, rates);
   Print("bars_copied=", copied);
   for(int i=0; i<copied; i++)
   {
      Print("bar[", i, "] time_epoch=", (long)rates[i].time,
            " time_text=", Ts(rates[i].time),
            " time_minus_TimeGMT_seconds=", (long)(rates[i].time-t_time_gmt),
            " time_minus_TimeTradeServer_seconds=", (long)(rates[i].time-t_time_trade_server));
   }

   Print("diagnostic=SOURCE_TIME_BASIS_ONLY; DO_NOT_SHIFT_DATA");
}
