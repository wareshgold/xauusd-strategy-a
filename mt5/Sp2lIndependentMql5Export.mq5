#property strict
#property script_show_inputs

input string InpSymbol = "XAUUSD.ecn";
input ENUM_TIMEFRAMES InpTimeframe = PERIOD_M1;
input datetime InpStart = D'2026.09.18 13:11:00';
input datetime InpEnd   = D'2026.09.18 23:57:00';
input string InpFileName = "sp2l_mt5_independent_export_2026-09-18.csv";

void OnStart()
{
   if(InpEnd < InpStart)
   {
      Print("FAIL: end before start");
      return;
   }

   MqlRates rates[];
   int copied = CopyRates(InpSymbol, InpTimeframe, InpStart, InpEnd, rates);
   if(copied <= 0)
   {
      PrintFormat("FAIL: CopyRates returned %d, error=%d", copied, GetLastError());
      return;
   }

   ArraySetAsSeries(rates, false);

   int handle = FileOpen(InpFileName, FILE_WRITE|FILE_CSV|FILE_ANSI, ',');
   if(handle == INVALID_HANDLE)
   {
      PrintFormat("FAIL: FileOpen error=%d", GetLastError());
      return;
   }

   FileWrite(handle, "time_epoch","time_terminal","open","high","low","close","tick_volume","spread","real_volume");

   for(int i = 0; i < copied; i++)
   {
      FileWrite(handle,
                (long)rates[i].time,
                TimeToString(rates[i].time, TIME_DATE|TIME_SECONDS),
                DoubleToString(rates[i].open, _Digits),
                DoubleToString(rates[i].high, _Digits),
                DoubleToString(rates[i].low, _Digits),
                DoubleToString(rates[i].close, _Digits),
                (long)rates[i].tick_volume,
                (int)rates[i].spread,
                (long)rates[i].real_volume);
   }

   FileClose(handle);

   PrintFormat("EXPORT_OK symbol=%s timeframe=M1 requested_start=%s requested_end=%s copied=%d first=%s last=%s file=%s",
               InpSymbol,
               TimeToString(InpStart, TIME_DATE|TIME_SECONDS),
               TimeToString(InpEnd, TIME_DATE|TIME_SECONDS),
               copied,
               TimeToString(rates[0].time, TIME_DATE|TIME_SECONDS),
               TimeToString(rates[copied-1].time, TIME_DATE|TIME_SECONDS),
               InpFileName);
}
