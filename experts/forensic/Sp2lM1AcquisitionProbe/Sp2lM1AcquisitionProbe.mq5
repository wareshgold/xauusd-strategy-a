//+------------------------------------------------------------------+
//| SP2L M1 History Acquisition Probe                                |
//| NON_CANONICAL_FORENSIC - data acquisition only                   |
//| No Strategy A geometry, signals, trades, or performance logic.   |
//+------------------------------------------------------------------+
#property strict
#property version "1.0"

input group "Historical M1 Acquisition Probe"
input datetime InpStartUTC = D'2025.09.25 00:00:00';
input datetime InpEndUTC   = D'2026.09.25 00:00:00';
input string   InpSymbol   = "";

struct WindowSpec {
   string name;
   datetime start_utc;
   datetime end_utc;
};

string CsvTime(datetime t) {
   return TimeToString(t,TIME_DATE|TIME_MINUTES|TIME_SECONDS);
}

string SafeName(string s) {
   StringReplace(s," ","_");
   StringReplace(s,":","-");
   return s;
}

void ProbeWindow(const WindowSpec &w,int index,int file_handle) {
   MqlRates rates[];
   ArraySetAsSeries(rates,false);
   ResetLastError();
   int copied=CopyRates(_Symbol,PERIOD_M1,w.start_utc,w.end_utc,rates);
   int err=GetLastError();

   datetime first=0,last=0;
   if(copied>0) {
      first=rates[0].time;
      last=rates[copied-1].time;
   }

   string first_s=copied>0 ? CsvTime(first) : "";
   string last_s=copied>0 ? CsvTime(last) : "";

   Print("WINDOW index=",index,
         " name=",w.name,
         " requested_start_utc=",CsvTime(w.start_utc),
         " requested_end_utc=",CsvTime(w.end_utc),
         " copied=",copied,
         " copy_error=",err,
         " first_utc=",first_s,
         " last_utc=",last_s);

   bool start_ok=(copied>0 && first<=w.start_utc);
   bool end_ok=(copied>0 && last>=w.end_utc-60);
   bool full_ok=(start_ok && end_ok);

   Print("WINDOW_COVERAGE index=",index,
         " name=",w.name,
         " start_covered=",start_ok ? "true":"false",
         " end_covered=",end_ok ? "true":"false",
         " full_window_covered=",full_ok ? "true":"false");

   if(file_handle!=INVALID_HANDLE) {
      FileWrite(file_handle,
         index,w.name,
         (long)w.start_utc,(long)w.end_utc,
         copied,err,
         (long)first,(long)last,
         start_ok ? "true":"false",
         end_ok ? "true":"false",
         full_ok ? "true":"false");
   }
}

int OnInit() {
   string symbol=InpSymbol;
   if(symbol=="") symbol=_Symbol;

   if(symbol!=_Symbol) {
      Print("SYMBOL_MISMATCH_PROBE_EA_SYMBOL=",_Symbol,
            " requested_symbol=",symbol,
            " NOTE=Tester symbol is authoritative; no cross-symbol acquisition attempted");
   }

   Print("ACQUISITION_PROBE_START symbol=",_Symbol,
         " period=M1 start_utc=",CsvTime(InpStartUTC),
         " end_utc=",CsvTime(InpEndUTC));

   MqlRates full_rates[];
   ArraySetAsSeries(full_rates,false);
   ResetLastError();
   int full_copied=CopyRates(_Symbol,PERIOD_M1,InpStartUTC,InpEndUTC,full_rates);
   int full_err=GetLastError();

   Print("FULL_WINDOW copied=",full_copied,
         " copy_error=",full_err,
         " first_utc=",full_copied>0 ? CsvTime(full_rates[0].time) : "",
         " last_utc=",full_copied>0 ? CsvTime(full_rates[full_copied-1].time) : "");

   string filename="SP2L_M1_ACQUISITION_PROBE_"+IntegerToString((long)InpStartUTC)+"_"+IntegerToString((long)InpEndUTC)+".csv";
   int h=FileOpen(filename,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
   if(h==INVALID_HANDLE) {
      Print("PROBE_FILE_OPEN_FAILED err=",GetLastError()," file=",filename);
      return INIT_FAILED;
   }

   FileWrite(h,"index","window_name","start_epoch_utc","end_epoch_utc",
             "copied","copy_error","first_epoch_utc","last_epoch_utc",
             "start_covered","end_covered","full_window_covered");

   WindowSpec windows[4];
   windows[0].name="W1_SEP_DEC_2025";
   windows[0].start_utc=D'2025.09.25 00:00:00';
   windows[0].end_utc=D'2026.01.01 00:00:00';

   windows[1].name="W2_JAN_MAR_2026";
   windows[1].start_utc=D'2026.01.01 00:00:00';
   windows[1].end_utc=D'2026.04.01 00:00:00';

   windows[2].name="W3_APR_JUN_2026";
   windows[2].start_utc=D'2026.04.01 00:00:00';
   windows[2].end_utc=D'2026.07.01 00:00:00';

   windows[3].name="W4_JUL_SEP_2026";
   windows[3].start_utc=D'2026.07.01 00:00:00';
   windows[3].end_utc=D'2026.09.25 00:00:00';

   for(int i=0;i<4;i++)
      ProbeWindow(windows[i],i+1,h);

   FileClose(h);
   Print("OUTPUT_PROBE_CSV=",filename);
   Print("ACQUISITION_PROBE_END canonical=false strategy_logic=false");
   return INIT_SUCCEEDED;
}

void OnTick() {}
void OnDeinit(const int reason) {}
