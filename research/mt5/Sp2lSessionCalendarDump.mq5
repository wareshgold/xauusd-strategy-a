#property script_show_inputs
#property strict

input string InpSymbol = "XAUUSD.ecn";
input int    InpMaxSessionsPerDay = 32;

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

void WriteSessionRow(const int handle,
                     const string kind,
                     const ENUM_DAY_OF_WEEK day,
                     const uint index,
                     const datetime from_time,
                     const datetime to_time)
{
   FileWrite(handle,
             kind,
             DayName(day),
             IntegerToString((int)day),
             IntegerToString((int)index),
             IntegerToString((int)from_time),
             IntegerToString((int)to_time),
             TimeToString(from_time, TIME_DATE|TIME_SECONDS),
             TimeToString(to_time, TIME_DATE|TIME_SECONDS));
}

void OnStart()
{
   if(!SymbolSelect(InpSymbol, true))
   {
      PrintFormat("SP2L_MT5_SESSION_CALENDAR_ERROR symbol_select symbol=%s error=%d",
                  InpSymbol, GetLastError());
      return;
   }

   string safe_symbol = InpSymbol;
   StringReplace(safe_symbol, ".", "_");
   StringReplace(safe_symbol, "/", "_");

   string stamp = TimeLocalToString(TimeLocal());
   StringReplace(stamp, ".", "-");
   StringReplace(stamp, ":", "-");
   StringReplace(stamp, " ", "T");

   string filename = StringFormat("sp2l_mt5_session_calendar_%s_%s.csv", safe_symbol, stamp);
   int handle = FileOpen(filename,
                         FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON,
                         ',');
   if(handle == INVALID_HANDLE)
   {
      PrintFormat("SP2L_MT5_SESSION_CALENDAR_ERROR file_open file=%s error=%d",
                  filename, GetLastError());
      return;
   }

   FileWrite(handle,
             "kind",
             "day_name",
             "day_enum",
             "session_index",
             "from_seconds_from_midnight",
             "to_seconds_from_midnight",
             "from_time",
             "to_time");

   PrintFormat("SP2L_MT5_SESSION_CALENDAR_BEGIN symbol=%s server_time=%s gmt_time=%s file=%s",
               InpSymbol,
               TimeToString(TimeTradeServer(), TIME_DATE|TIME_SECONDS),
               TimeToString(TimeGMT(), TIME_DATE|TIME_SECONDS),
               filename);

   int trade_count = 0;
   int quote_count = 0;

   for(int d = SUNDAY; d <= SATURDAY; d++)
   {
      ENUM_DAY_OF_WEEK day = (ENUM_DAY_OF_WEEK)d;

      for(uint i = 0; i < (uint)InpMaxSessionsPerDay; i++)
      {
         datetime from_time = 0;
         datetime to_time = 0;
         ResetLastError();
         if(!SymbolInfoSessionTrade(InpSymbol, day, i, from_time, to_time))
            break;
         WriteSessionRow(handle, "TRADE", day, i, from_time, to_time);
         trade_count++;
      }

      for(uint i = 0; i < (uint)InpMaxSessionsPerDay; i++)
      {
         datetime from_time = 0;
         datetime to_time = 0;
         ResetLastError();
         if(!SymbolInfoSessionQuote(InpSymbol, day, i, from_time, to_time))
            break;
         WriteSessionRow(handle, "QUOTE", day, i, from_time, to_time);
         quote_count++;
      }
   }

   FileClose(handle);

   PrintFormat("SP2L_MT5_SESSION_CALENDAR_END symbol=%s trade_rows=%d quote_rows=%d file=%s",
               InpSymbol, trade_count, quote_count, filename);
   Print("SP2L_MT5_SESSION_CALENDAR_NOTE: output preserves MT5 session timestamps as returned by the terminal; values are seconds from midnight and no UTC conversion, DST normalization, or session interpretation is performed.");
}
