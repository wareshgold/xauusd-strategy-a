#property strict
#property script_show_inputs

input string InpSymbol = "XAUUSD.ecn";

string DayName(const ENUM_DAY_OF_WEEK day)
{
   switch(day)
   {
      case SUNDAY:    return "SUNDAY";
      case MONDAY:    return "MONDAY";
      case TUESDAY:   return "TUESDAY";
      case WEDNESDAY: return "WEDNESDAY";
      case THURSDAY:  return "THURSDAY";
      case FRIDAY:    return "FRIDAY";
      case SATURDAY:  return "SATURDAY";
   }
   return "UNKNOWN";
}

void DumpSessions(const string symbol, const ENUM_DAY_OF_WEEK day, const bool quote)
{
   for(uint index = 0; index < 32; ++index)
   {
      datetime from = 0;
      datetime to = 0;
      bool ok = false;

      if(quote)
         ok = SymbolInfoSessionQuote(symbol, day, index, from, to);
      else
         ok = SymbolInfoSessionTrade(symbol, day, index, from, to);

      if(!ok)
         break;

      PrintFormat("%s|%s|session_index=%u|from=%s|to=%s|from_epoch=%I64d|to_epoch=%I64d",
                  quote ? "QUOTE" : "TRADE",
                  DayName(day),
                  index,
                  TimeToString(from, TIME_DATE|TIME_SECONDS),
                  TimeToString(to, TIME_DATE|TIME_SECONDS),
                  (long)from,
                  (long)to);
   }
}

void OnStart()
{
   Print("=== MT5 SESSION SCHEDULE DIAGNOSTIC ===");
   PrintFormat("terminal=%s", TerminalInfoString(TERMINAL_NAME));
   PrintFormat("company=%s", TerminalInfoString(TERMINAL_COMPANY));
   PrintFormat("server=%s", AccountInfoString(ACCOUNT_SERVER));
   PrintFormat("symbol=%s", InpSymbol);
   Print("SOURCE_MODEL=TERMINAL_SYMBOL_SESSION_SCHEDULE");
   Print("SEMANTICS=SESSION_TIMES_ARE_BROKER_SERVER_TIME_PER_MQL5_ALGOBOOK");
   Print("NO_BAR_TIMESTAMP_SHIFT=TRUE");

   if(!SymbolSelect(InpSymbol, true))
   {
      PrintFormat("symbol_select_failed=%d", GetLastError());
      return;
   }

   for(int day = MONDAY; day <= SUNDAY; ++day)
   {
      ENUM_DAY_OF_WEEK d = (ENUM_DAY_OF_WEEK)day;
      DumpSessions(InpSymbol, d, true);
      DumpSessions(InpSymbol, d, false);
   }

   Print("DIAGNOSTIC=SESSION_SCHEDULE_OBSERVATION_ONLY");
   Print("DO_NOT_INFER_HISTORICAL_CALENDAR_FROM_THIS_CURRENT_SNAPSHOT");
   Print("DO_NOT_SHIFT_CANONICAL_BAR_TIMESTAMPS");
}
