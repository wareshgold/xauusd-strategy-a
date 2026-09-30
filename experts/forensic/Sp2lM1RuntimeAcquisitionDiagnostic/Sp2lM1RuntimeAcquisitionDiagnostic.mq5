//+------------------------------------------------------------------+
//| SP2L M1 Runtime Acquisition Diagnostic                            |
//| NON_CANONICAL_FORENSIC - data acquisition only                   |
//| No Strategy A geometry, signals, trades, or performance logic.   |
//+------------------------------------------------------------------+
#property strict
#property version "2.0"

input group "Runtime M1 Acquisition Diagnostic"
input datetime InpStartUTC = D'2025.09.25 00:00:00';
input datetime InpEndUTC   = D'2026.09.25 00:00:00';
input datetime InpProbeUTC1 = D'2026.01.02 00:05:00';
input datetime InpProbeUTC2 = D'2026.06.20 00:05:00';
input datetime InpProbeUTC3 = D'2026.09.24 23:55:00';

bool ProbeAt(datetime requested_start,datetime requested_end,string label) {
   MqlRates rates[];
   ArraySetAsSeries(rates,false);
   ResetLastError();
   int copied=CopyRates(_Symbol,PERIOD_M1,requested_start,requested_end,rates);
   int err=GetLastError();

   datetime first=0,last=0;
   if(copied>0) {
      first=rates[0].time;
      last=rates[copied-1].time;
   }

   bool start_ok=(copied>0 && first<=requested_start);
   bool end_ok=(copied>0 && last>=requested_end-60);

   Print("BOUNDED_PROBE label=",label,
         " requested_start=",TimeToString(requested_start,TIME_DATE|TIME_MINUTES|TIME_SECONDS),
         " requested_end=",TimeToString(requested_end,TIME_DATE|TIME_MINUTES|TIME_SECONDS),
         " copied=",copied,
         " copy_error=",err,
         " first_utc=",copied>0 ? TimeToString(first,TIME_DATE|TIME_MINUTES|TIME_SECONDS) : "",
         " last_utc=",copied>0 ? TimeToString(last,TIME_DATE|TIME_MINUTES|TIME_SECONDS) : "",
         " start_covered=",start_ok ? "true":"false",
         " end_covered=",end_ok ? "true":"false");

   return (copied>0);
}

int OnInit() {
   Print("BOUNDED_RUNTIME_ACQUISITION_START symbol=",_Symbol,
         " tester_time=",TimeToString(TimeCurrent(),TIME_DATE|TIME_MINUTES|TIME_SECONDS));

   // These probes deliberately use small, local windows around dates that
   // distinguish the known Dec-2025 M1 boundary from 2026 availability.
   ProbeAt(D'2025.12.31 23:55:00',D'2026.01.01 00:05:00',"BOUNDARY_DEC_JAN");
   ProbeAt(D'2026.01.02 00:00:00',D'2026.01.02 00:10:00',"JAN_2026");
   ProbeAt(D'2026.06.20 00:00:00',D'2026.06.20 00:10:00',"JUN_2026");
   ProbeAt(D'2026.09.24 23:50:00',D'2026.09.25 00:00:00',"SEP_2026");

   Print("BOUNDED_RUNTIME_ACQUISITION_END canonical=false strategy_logic=false");
   return INIT_SUCCEEDED;
}

void OnTick() {}
