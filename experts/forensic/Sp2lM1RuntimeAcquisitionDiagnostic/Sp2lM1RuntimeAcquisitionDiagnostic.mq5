//+------------------------------------------------------------------+
//| SP2L M1 Runtime Acquisition Diagnostic                            |
//| NON_CANONICAL_FORENSIC - data acquisition only                   |
//| No Strategy A geometry, signals, trades, or performance logic.   |
//+------------------------------------------------------------------+
#property strict
#property version "1.0"

input group "Runtime M1 Acquisition Diagnostic"
input datetime InpStartUTC = D'2025.09.25 00:00:00';
input datetime InpEndUTC   = D'2026.09.25 00:00:00';
input int InpProbeEverySeconds = 60;

datetime g_last_probe=0;
bool g_done=false;

string Ts(datetime t) { return TimeToString(t,TIME_DATE|TIME_MINUTES|TIME_SECONDS); }

void ProbeAt(datetime sim_time,string label) {
   MqlRates rates[];
   ArraySetAsSeries(rates,false);
   ResetLastError();
   int copied=CopyRates(_Symbol,PERIOD_M1,InpStartUTC,InpEndUTC,rates);
   int err=GetLastError();

   datetime first=0,last=0;
   if(copied>0) {
      first=rates[0].time;
      last=rates[copied-1].time;
   }

   bool start_ok=(copied>0 && first<=InpStartUTC);
   bool end_ok=(copied>0 && last>=InpEndUTC-60);
   Print("RUNTIME_PROBE label=",label,
         " sim_time=",Ts(sim_time),
         " requested_start=",Ts(InpStartUTC),
         " requested_end=",Ts(InpEndUTC),
         " copied=",copied,
         " copy_error=",err,
         " first_utc=",copied>0 ? Ts(first) : "",
         " last_utc=",copied>0 ? Ts(last) : "",
         " start_covered=",start_ok ? "true":"false",
         " end_covered=",end_ok ? "true":"false");
}

int OnInit() {
   EventSetTimer(InpProbeEverySeconds>0 ? InpProbeEverySeconds : 60);
   Print("RUNTIME_ACQUISITION_DIAGNOSTIC_START symbol=",_Symbol,
         " period=M1 start_utc=",Ts(InpStartUTC),
         " end_utc=",Ts(InpEndUTC));
   ProbeAt(TimeCurrent(),"INIT");
   return INIT_SUCCEEDED;
}

void OnTick() {
   datetime now=TimeCurrent();
   if(g_done) return;

   // Probe on each new simulated minute so we observe acquisition as the
   // Tester advances through the requested historical interval.
   static datetime last_bar=0;
   MqlRates bar[];
   ArraySetAsSeries(bar,true);
   if(CopyRates(_Symbol,PERIOD_M1,0,1,bar)==1) {
      if(bar[0].time!=last_bar) {
         last_bar=bar[0].time;
         if(now>=InpStartUTC && now<=InpEndUTC)
            ProbeAt(now,"NEW_M1_BAR");
      }
   }

   if(now>=InpEndUTC) {
      ProbeAt(now,"END_REACHED");
      g_done=true;
   }
}

void OnTimer() {
   datetime now=TimeCurrent();
   if(!g_done && now>=InpStartUTC && now<=InpEndUTC)
      ProbeAt(now,"TIMER");
}

void OnDeinit(const int reason) {
   EventKillTimer();
   Print("RUNTIME_ACQUISITION_DIAGNOSTIC_END canonical=false strategy_logic=false");
}
