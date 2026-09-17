//+------------------------------------------------------------------+
//| mt5_mql5_symbol_session_metadata.mq5                              |
//| Diagnostic only: inspect broker-provided quote/trade sessions.   |
//| No data transformation, inference, or acquisition policy.       |
//+------------------------------------------------------------------+
#property script_show_inputs

input string InpSymbol = "XAUUSD.ecn";
input int    InpMaxSessionsPerDay = 16;

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

void PrintSession(const string kind,
                  const ENUM_DAY_OF_WEEK day,
                  const uint index,
                  const bool ok,
                  const datetime from,
                  const datetime to)
  {
   if(ok)
      PrintFormat("SESSION|type=%s|day=%s|index=%u|from=%s|to=%s",
                  kind,
                  DayName(day),
                  index,
                  TimeToString(from,TIME_MINUTES|TIME_SECONDS),
                  TimeToString(to,TIME_MINUTES|TIME_SECONDS));
  }

void ProbeQuote(const ENUM_DAY_OF_WEEK day)
  {
   for(uint index=0; index<(uint)InpMaxSessionsPerDay; index++)
     {
      datetime from=0, to=0;
      ResetLastError();
      bool ok=SymbolInfoSessionQuote(InpSymbol,day,index,from,to);
      int err=GetLastError();
      if(!ok)
        {
         PrintFormat("SESSION_PROBE_END|type=QUOTE|day=%s|index=%u|error=%d",
                     DayName(day),index,err);
         break;
        }
      PrintSession("QUOTE",day,index,ok,from,to);
     }
  }

void ProbeTrade(const ENUM_DAY_OF_WEEK day)
  {
   for(uint index=0; index<(uint)InpMaxSessionsPerDay; index++)
     {
      datetime from=0, to=0;
      ResetLastError();
      bool ok=SymbolInfoSessionTrade(InpSymbol,day,index,from,to);
      int err=GetLastError();
      if(!ok)
        {
         PrintFormat("SESSION_PROBE_END|type=TRADE|day=%s|index=%u|error=%d",
                     DayName(day),index,err);
         break;
        }
      PrintSession("TRADE",day,index,ok,from,to);
     }
  }

void OnStart()
  {
   Print("SESSION_DIAGNOSTIC_BEGIN|symbol=",InpSymbol);
   Print("SESSION_DIAGNOSTIC|terminal=",TerminalInfoString(TERMINAL_NAME),
         "|company=",AccountInfoString(ACCOUNT_COMPANY),
         "|server=",AccountInfoString(ACCOUNT_SERVER));
   Print("SESSION_DIAGNOSTIC|symbol_selected=",(bool)SymbolSelect(InpSymbol,true));
   Print("SESSION_DIAGNOSTIC|symbol_exists=",SymbolExist(InpSymbol,true));

   for(int day=(int)SUNDAY; day<=(int)SATURDAY; day++)
     {
      ENUM_DAY_OF_WEEK dow=(ENUM_DAY_OF_WEEK)day;
      Print("DAY_BEGIN|",DayName(dow));
      ProbeQuote(dow);
      ProbeTrade(dow);
      Print("DAY_END|",DayName(dow));
     }

   Print("SESSION_DIAGNOSTIC_END|symbol=",InpSymbol);
  }
//+------------------------------------------------------------------+
