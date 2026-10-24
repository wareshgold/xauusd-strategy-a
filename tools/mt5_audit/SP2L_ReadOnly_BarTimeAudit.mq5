#property strict
#property script_show_inputs

input string InpSymbol = "XAUUSD.ecn";

// Window A: the timestamps reported in the CSV/chart.
input datetime InpWindowAFrom = D'2026.10.20 23:45:00';
input datetime InpWindowATo   = D'2026.10.21 01:15:00';

// Window B: same dates shifted by three hours, to test the alternative mapping.
input datetime InpWindowBFrom = D'2026.10.21 02:45:00';
input datetime InpWindowBTo   = D'2026.10.21 04:15:00';

bool IsBoundaryBar(const MqlDateTime &dt)
{
   // Print a compact sample around midnight and the expected 01:00 reopen.
   if(dt.hour == 23 && dt.min >= 53) return true;
   if(dt.hour == 0  && dt.min <= 5)  return true;
   if(dt.hour == 1  && dt.min <= 5)  return true;
   if(dt.hour == 2  && dt.min >= 53) return true;
   if(dt.hour == 3  && dt.min <= 5)  return true;
   if(dt.hour == 4  && dt.min <= 5)  return true;
   return false;
}

void AuditWindow(const string label, const datetime from_time, const datetime to_time)
{
   Print("----- WINDOW ", label, " -----");
   Print("QUERY_FROM=", TimeToString(from_time, TIME_DATE|TIME_SECONDS),
         " QUERY_TO=", TimeToString(to_time, TIME_DATE|TIME_SECONDS));

   MqlRates rates[];
   ArraySetAsSeries(rates, false);
   ResetLastError();
   int count = CopyRates(InpSymbol, PERIOD_M1, from_time, to_time, rates);
   int err = GetLastError();

   Print("COPYRATES_COUNT=", count, " LAST_ERROR=", err);
   if(count <= 0)
   {
      Print("NO_RATES_RETURNED; ensure symbol history is available, then rerun.");
      return;
   }

   for(int i = 0; i < count; i++)
   {
      MqlDateTime dt;
      if(!TimeToStruct(rates[i].time, dt))
         continue;
      if(!IsBoundaryBar(dt))
         continue;

      Print("BAR time=", TimeToString(rates[i].time, TIME_DATE|TIME_SECONDS),
            " datetime_value=", (long)rates[i].time,
            " O=", DoubleToString(rates[i].open, 2),
            " H=", DoubleToString(rates[i].high, 2),
            " L=", DoubleToString(rates[i].low, 2),
            " C=", DoubleToString(rates[i].close, 2),
            " tick_volume=", (long)rates[i].tick_volume);
   }
}

void OnStart()
{
   Print("========== SP2L READ-ONLY BAR TIME AUDIT ==========");
   Print("SYMBOL=", InpSymbol);
   Print("TimeGMT=", TimeToString(TimeGMT(), TIME_DATE|TIME_SECONDS));
   Print("TimeTradeServer=", TimeToString(TimeTradeServer(), TIME_DATE|TIME_SECONDS));
   Print("TimeCurrent_last_quote=", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS));
   Print("NOTE: query datetime labels are tested as supplied; this script does not convert or shift timestamps.");
   Print("NOTE: datetime_value is printed for comparison, not asserted to be UTC.");

   if(!SymbolSelect(InpSymbol, true))
   {
      Print("SYMBOL_SELECT_FAILED error=", GetLastError());
      Print("========== AUDIT STOPPED ==========");
      return;
   }

   AuditWindow("A_REPORTED_LABELS", InpWindowAFrom, InpWindowATo);
   AuditWindow("B_PLUS_3_HOURS", InpWindowBFrom, InpWindowBTo);

   Print("========== AUDIT COMPLETE: NO TRADES OR DATA WRITES ==========");
}
