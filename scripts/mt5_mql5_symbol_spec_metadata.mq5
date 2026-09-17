//+------------------------------------------------------------------+
//| mt5_mql5_symbol_spec_metadata.mq5                                |
//| Diagnostic only: capture broker/terminal symbol specification.   |
//| No strategy logic, inference, acquisition, or order placement.  |
//+------------------------------------------------------------------+
#property script_show_inputs

input string InpSymbol = "XAUUSD.ecn";

void PrintInt(const string key, const long value)
  {
   PrintFormat("SPEC_INT|key=%s|value=%I64d",key,value);
  }

void PrintDouble(const string key, const double value)
  {
   PrintFormat("SPEC_DOUBLE|key=%s|value=%.10f",key,value);
  }

void PrintString(const string key, const string value)
  {
   PrintFormat("SPEC_STRING|key=%s|value=%s",key,value);
  }

void OnStart()
  {
   ResetLastError();

   bool custom=false;
   bool exists=SymbolExist(InpSymbol,custom);
   bool selected=SymbolSelect(InpSymbol,true);

   Print("SPEC_DIAGNOSTIC_BEGIN|symbol=",InpSymbol);
   PrintString("terminal_name",TerminalInfoString(TERMINAL_NAME));
   PrintString("terminal_company",AccountInfoString(ACCOUNT_COMPANY));
   PrintString("account_server",AccountInfoString(ACCOUNT_SERVER));
   PrintInt("terminal_build",TerminalInfoInteger(TERMINAL_BUILD));
   PrintInt("terminal_trade_allowed",TerminalInfoInteger(TERMINAL_TRADE_ALLOWED));
   PrintInt("symbol_exists",(long)exists);
   PrintInt("symbol_custom",(long)custom);
   PrintInt("symbol_selected",(long)selected);

   if(!exists || !selected)
     {
      PrintFormat("SPEC_DIAGNOSTIC_FAIL|last_error=%d",GetLastError());
      return;
     }

   // Identity / descriptive fields.
   PrintString("path",SymbolInfoString(InpSymbol,SYMBOL_PATH));
   PrintString("description",SymbolInfoString(InpSymbol,SYMBOL_DESCRIPTION));
   PrintString("currency_base",SymbolInfoString(InpSymbol,SYMBOL_CURRENCY_BASE));
   PrintString("currency_profit",SymbolInfoString(InpSymbol,SYMBOL_CURRENCY_PROFIT));
   PrintString("currency_margin",SymbolInfoString(InpSymbol,SYMBOL_CURRENCY_MARGIN));

   // Market / trading modes.
   PrintInt("trade_mode",SymbolInfoInteger(InpSymbol,SYMBOL_TRADE_MODE));
   PrintInt("trade_calc_mode",SymbolInfoInteger(InpSymbol,SYMBOL_TRADE_CALC_MODE));
   PrintInt("trade_execution",SymbolInfoInteger(InpSymbol,SYMBOL_TRADE_EXEMODE));
   PrintInt("filling_mode",SymbolInfoInteger(InpSymbol,SYMBOL_FILLING_MODE));
   PrintInt("order_mode",SymbolInfoInteger(InpSymbol,SYMBOL_ORDER_MODE));
   PrintInt("expiration_mode",SymbolInfoInteger(InpSymbol,SYMBOL_EXPIRATION_MODE));
   PrintInt("order_gtc_mode",SymbolInfoInteger(InpSymbol,SYMBOL_ORDER_GTC_MODE));

   // Price / contract specification.
   PrintInt("digits",SymbolInfoInteger(InpSymbol,SYMBOL_DIGITS));
   PrintInt("spread_points",SymbolInfoInteger(InpSymbol,SYMBOL_SPREAD));
   PrintInt("spread_float",SymbolInfoInteger(InpSymbol,SYMBOL_SPREAD_FLOAT));
   PrintInt("stops_level_points",SymbolInfoInteger(InpSymbol,SYMBOL_TRADE_STOPS_LEVEL));
   PrintInt("freeze_level_points",SymbolInfoInteger(InpSymbol,SYMBOL_TRADE_FREEZE_LEVEL));
   PrintDouble("point",SymbolInfoDouble(InpSymbol,SYMBOL_POINT));
   PrintDouble("tick_size",SymbolInfoDouble(InpSymbol,SYMBOL_TRADE_TICK_SIZE));
   PrintDouble("tick_value",SymbolInfoDouble(InpSymbol,SYMBOL_TRADE_TICK_VALUE));
   PrintDouble("tick_value_profit",SymbolInfoDouble(InpSymbol,SYMBOL_TRADE_TICK_VALUE_PROFIT));
   PrintDouble("tick_value_loss",SymbolInfoDouble(InpSymbol,SYMBOL_TRADE_TICK_VALUE_LOSS));
   PrintDouble("contract_size",SymbolInfoDouble(InpSymbol,SYMBOL_TRADE_CONTRACT_SIZE));
   PrintDouble("volume_min",SymbolInfoDouble(InpSymbol,SYMBOL_VOLUME_MIN));
   PrintDouble("volume_max",SymbolInfoDouble(InpSymbol,SYMBOL_VOLUME_MAX));
   PrintDouble("volume_step",SymbolInfoDouble(InpSymbol,SYMBOL_VOLUME_STEP));
   PrintDouble("volume_limit",SymbolInfoDouble(InpSymbol,SYMBOL_VOLUME_LIMIT));

   // Current quote snapshot (observation only; not a strategy signal).
   MqlTick tick;
   if(SymbolInfoTick(InpSymbol,tick))
     {
      PrintString("tick_time",TimeToString(tick.time,TIME_DATE|TIME_SECONDS));
      PrintDouble("tick_bid",tick.bid);
      PrintDouble("tick_ask",tick.ask);
      PrintDouble("tick_last",tick.last);
      PrintDouble("tick_volume",(double)tick.volume);
     }
   else
      PrintFormat("SPEC_TICK_FAIL|last_error=%d",GetLastError());

   Print("SPEC_DIAGNOSTIC_END|symbol=",InpSymbol);
  }
//+------------------------------------------------------------------+
