#property strict
#property version   "1.0"

input long InpStartUTC = 1758758400; // 2025-09-25 00:00:00 UTC
input long InpEndUTC   = 1790294400; // 2026-09-25 00:00:00 UTC
input string InpOutputFile = "sp2l_runtime_m1_20250925_20260925.csv";

int g_handle = INVALID_HANDLE;
datetime g_last_minute = 0;
long g_rows = 0;
long g_copy_errors = 0;
datetime g_first_bar = 0;
datetime g_last_bar = 0;

bool InRange(const datetime t)
{
   return ((long)t >= InpStartUTC && (long)t < InpEndUTC);
}

void WriteBar(const datetime bar_time)
{
   if(!InRange(bar_time))
      return;

   MqlRates rates[1];
   ResetLastError();
   int copied = CopyRates(_Symbol, PERIOD_M1, bar_time, 1, rates);
   if(copied != 1 || rates[0].time != bar_time)
   {
      g_copy_errors++;
      PrintFormat("EXPORT_COPY_ERROR bar=%s copied=%d err=%d",
                  TimeToString(bar_time, TIME_DATE|TIME_MINUTES|TIME_SECONDS),
                  copied, GetLastError());
      return;
   }

   FileWrite(g_handle,
             (long)rates[0].time,
             TimeToString(rates[0].time, TIME_DATE|TIME_MINUTES),
             DoubleToString(rates[0].open, _Digits),
             DoubleToString(rates[0].high, _Digits),
             DoubleToString(rates[0].low, _Digits),
             DoubleToString(rates[0].close, _Digits),
             (long)rates[0].tick_volume,
             (long)rates[0].real_volume,
             (long)rates[0].spread);

   g_rows++;
   if(g_first_bar == 0)
      g_first_bar = rates[0].time;
   g_last_bar = rates[0].time;
}

int OnInit()
{
   if(InpEndUTC <= InpStartUTC)
   {
      Print("EXPORT_INVALID_RANGE");
      return INIT_PARAMETERS_INCORRECT;
   }

   g_handle = FileOpen(InpOutputFile,
                       FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI,
                       ',');

   if(g_handle == INVALID_HANDLE)
   {
      PrintFormat("EXPORT_FILE_OPEN_ERROR err=%d file=%s",
                  GetLastError(), InpOutputFile);
      return INIT_FAILED;
   }

   FileWrite(g_handle,
             "epoch_utc",
             "time_utc",
             "open",
             "high",
             "low",
             "close",
             "tick_volume",
             "real_volume",
             "spread");

   PrintFormat("RUNTIME_M1_EXPORT_START symbol=%s start=%s end=%s file=%s",
               _Symbol,
               TimeToString((datetime)InpStartUTC, TIME_DATE|TIME_MINUTES|TIME_SECONDS),
               TimeToString((datetime)InpEndUTC, TIME_DATE|TIME_MINUTES|TIME_SECONDS),
               InpOutputFile);

   return INIT_SUCCEEDED;
}

void OnTick()
{
   const datetime tick_time = (datetime)TimeCurrent();
   if(tick_time < (datetime)InpStartUTC)
      return;

   if(tick_time >= (datetime)InpEndUTC)
   {
      ExpertRemove();
      return;
   }

   const datetime minute = tick_time - (tick_time % 60);

   if(g_last_minute == 0)
   {
      g_last_minute = minute;
      return;
   }

   if(minute != g_last_minute)
   {
      WriteBar(g_last_minute);
      g_last_minute = minute;
   }
}

void OnDeinit(const int reason)
{
   if(g_last_minute != 0)
      WriteBar(g_last_minute);

   if(g_handle != INVALID_HANDLE)
   {
      FileFlush(g_handle);
      FileClose(g_handle);
      g_handle = INVALID_HANDLE;
   }

   PrintFormat("RUNTIME_M1_EXPORT_END canonical=false strategy_logic=false rows=%I64d copy_errors=%I64d first=%s last=%s reason=%d",
               g_rows,
               g_copy_errors,
               TimeToString(g_first_bar, TIME_DATE|TIME_MINUTES),
               TimeToString(g_last_bar, TIME_DATE|TIME_MINUTES),
               reason);
}
