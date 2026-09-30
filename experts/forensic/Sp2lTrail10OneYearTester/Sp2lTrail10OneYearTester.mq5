//+------------------------------------------------------------------+
//| SP2L Trail-10 One-Year MT5 forensic tester                       |
//| NON_CANONICAL_FORENSIC - research only                           |
//| Dedicated fixed-contract population/coverage experiment.         |
//+------------------------------------------------------------------+
#property strict
#property version "1.0"

input group "SP2L Trail-10 One-Year Fixed Contract"
input datetime InpStartUTC = D'2025.09.25 00:00:00'; // fixed research start (UTC)
input datetime InpEndUTC   = D'2026.09.25 00:00:00'; // fixed research end (UTC)
input double InpPGAP       = 1.0;
input double InpSpikeMult  = 1.5;
input double InpMaxSL      = 10.0;
input double InpRR         = 1.0;
input double InpTrailPips  = 10.0; // 1 pip = 0.10 XAU price
input double InpVolumeLots = 0.01;

datetime START_UTC;
datetime END_UTC;
double PGAP;
double SPIKE_MULT;
double MAX_SL;
double RR;
double TRAIL_PIPS;
double VOLUME_LOTS;

struct Signal {
   int setup_index;
   int entry_index;
   datetime setup_time;
   datetime entry_time;
   string direction;
   double entry;
   double sl;
   double risk;
};

MqlRates g_rates[];
Signal g_signals[];

double Body(const MqlRates &c,const string d) {
   return d=="BUY" ? c.close-c.open : c.open-c.close;
}

bool Setup(const int i,const string d) {
   if(i<2) return false;
   MqlRates before=g_rates[i-2], spike=g_rates[i-1], after=g_rates[i];

   if(d=="BUY")
      return after.close>spike.close && after.open>spike.open &&
             spike.close>before.close && spike.open>before.open &&
             after.close>after.open && spike.close>spike.open &&
             before.close>before.open && after.low>before.high+PGAP &&
             Body(spike,"BUY")>SPIKE_MULT*Body(before,"BUY") &&
             Body(spike,"BUY")>SPIKE_MULT*Body(after,"BUY");

   return after.close<spike.close && after.open<spike.open &&
          spike.close<before.close && spike.open<before.open &&
          after.close<after.open && spike.close<spike.open &&
          before.close<before.open && after.high<before.low-PGAP &&
          Body(spike,"SELL")>SPIKE_MULT*Body(before,"SELL") &&
          Body(spike,"SELL")>SPIKE_MULT*Body(after,"SELL");
}

bool BuildSignal(const int setup_index,Signal &out) {
   bool buy=Setup(setup_index,"BUY"), sell=Setup(setup_index,"SELL");
   if(buy==sell) return false;
   string d=buy ? "BUY" : "SELL";
   double sl=buy ? g_rates[setup_index-2].low : g_rates[setup_index-2].high;

   for(int j=setup_index+1;j<ArraySize(g_rates);j++) {
      double entry=buy ? g_rates[j].low : g_rates[j].high;
      bool trigger=buy ? entry<g_rates[j-1].low : entry>g_rates[j-1].high;
      if(!trigger) continue;
      double risk=buy ? entry-sl : sl-entry;
      if(risk<=0.0 || risk>MAX_SL) return false;
      out.setup_index=setup_index; out.entry_index=j;
      out.setup_time=g_rates[setup_index].time;
      out.entry_time=g_rates[j].time;
      out.direction=d; out.entry=entry; out.sl=sl; out.risk=risk;
      return true;
   }
   return false;
}

string ResultForSignal(const Signal &s,double &r,int &exit_i,bool &trail_active) {
   r=0.0; exit_i=-1; trail_active=false;
   double risk=MathAbs(s.entry-s.sl);
   double tp=s.direction=="BUY" ? s.entry+RR*risk : s.entry-RR*risk;
   double current_sl=s.sl, best=s.entry, trail=TRAIL_PIPS*0.10;

   for(int i=s.entry_index;i<ArraySize(g_rates);i++) {
      double high=g_rates[i].high, low=g_rates[i].low;
      if(s.direction=="BUY") {
         bool sl_hit=low<=current_sl, tp_hit=high>=tp;
         if(sl_hit && tp_hit) { exit_i=i; return "AMBIGUOUS"; }
         if(sl_hit) {
            r=(current_sl-s.entry)/risk; exit_i=i;
            if(r>0) return "WIN"; if(r<0) return "LOSS"; return "BREAKEVEN";
         }
         if(tp_hit) { r=RR; exit_i=i; return "WIN"; }
         best=MathMax(best,high);
         if(!trail_active && best>=s.entry+trail) trail_active=true;
         if(trail_active) current_sl=MathMax(current_sl,best-trail);
      } else {
         bool sl_hit=high>=current_sl, tp_hit=low<=tp;
         if(sl_hit && tp_hit) { exit_i=i; return "AMBIGUOUS"; }
         if(sl_hit) {
            r=(s.entry-current_sl)/risk; exit_i=i;
            if(r>0) return "WIN"; if(r<0) return "LOSS"; return "BREAKEVEN";
         }
         if(tp_hit) { r=RR; exit_i=i; return "WIN"; }
         best=MathMin(best,low);
         if(!trail_active && best<=s.entry-trail) trail_active=true;
         if(trail_active) current_sl=MathMin(current_sl,best+trail);
      }
   }
   return "OPEN_OR_UNRESOLVED";
}

string CsvTime(datetime t) { return TimeToString(t,TIME_DATE|TIME_MINUTES|TIME_SECONDS); }

void WriteText(const string filename,const string text) {
   int h=FileOpen(filename,FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(h==INVALID_HANDLE) { Print("FILE_OPEN_FAILED err=",GetLastError()," file=",filename); return; }
   FileWriteString(h,text); FileClose(h);
}

void ExportHistoryCsv() {
   string f="SP2L_TRAIL10_ONE_YEAR_HISTORY_1758758400_1790294400.csv";
   int h=FileOpen(f,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
   if(h==INVALID_HANDLE) { Print("HISTORY_FILE_OPEN_FAILED err=",GetLastError()); return; }
   FileWrite(h,"time_epoch_utc","open","high","low","close","tick_volume","spread","real_volume");
   for(int i=0;i<ArraySize(g_rates);i++)
      FileWrite(h,(long)g_rates[i].time,
                DoubleToString(g_rates[i].open,_Digits),DoubleToString(g_rates[i].high,_Digits),
                DoubleToString(g_rates[i].low,_Digits),DoubleToString(g_rates[i].close,_Digits),
                (long)g_rates[i].tick_volume,g_rates[i].spread,(long)g_rates[i].real_volume);
   FileClose(h);
   Print("OUTPUT_HISTORY_CSV=",f," bars=",ArraySize(g_rates));
}

int OnInit() {
   START_UTC=InpStartUTC;
   END_UTC=InpEndUTC;
   PGAP=InpPGAP;
   SPIKE_MULT=InpSpikeMult;
   MAX_SL=InpMaxSL;
   RR=InpRR;
   TRAIL_PIPS=InpTrailPips;
   VOLUME_LOTS=InpVolumeLots;

   ArraySetAsSeries(g_rates,false);
   ResetLastError();
   datetime start=(datetime)START_UTC, end=(datetime)END_UTC;
   int copied=CopyRates(_Symbol,PERIOD_M1,start,end,g_rates);
   int copy_error=GetLastError();

   Print("REQUESTED_HISTORY symbol=",_Symbol,
         " period=M1 start_utc=",CsvTime(start)," end_utc=",CsvTime(end),
         " copied=",copied," copy_error=",copy_error);

   if(copied<=0) { Print("COPY_RATES_FAILED"); return INIT_FAILED; }
   ArraySetAsSeries(g_rates,false);

   datetime first=g_rates[0].time, last=g_rates[copied-1].time;
   Print("ACTUAL_HISTORY symbol=",_Symbol,
         " bars=",copied," first_utc=",CsvTime(first)," last_utc=",CsvTime(last));

   if(first<start || last>=end)
      Print("COVERAGE_BOUNDARY_NOTE first_or_last_outside_expected_half_open_range");
   if(last<end-60)
      Print("COVERAGE_END_GAP_OR_HISTORY_LIMIT last_utc=",CsvTime(last),
            " expected_before=",CsvTime(end-60));

   ExportHistoryCsv();

   ArrayResize(g_signals,0);
   for(int i=2;i<copied;i++) {
      Signal s;
      if(BuildSignal(i,s)) {
         int n=ArraySize(g_signals); ArrayResize(g_signals,n+1); g_signals[n]=s;
      }
   }

   int signals=ArraySize(g_signals), wins=0, losses=0, be=0, amb=0, open=0, trail_count=0;
   double net_r=0,gp=0,gl=0,equity=0,peak=0,maxdd=0;
   int streak=0,maxstreak=0;

   string stamp=IntegerToString((int)TimeLocal());
   string trade_csv="SP2L_TRAIL10_ONE_YEAR_TRADES_"+stamp+".csv";
   string summary_txt="SP2L_TRAIL10_ONE_YEAR_SUMMARY_"+stamp+".txt";
   int h=FileOpen(trade_csv,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
   if(h==INVALID_HANDLE) { Print("TRADE_FILE_OPEN_FAILED err=",GetLastError()); return INIT_FAILED; }

   FileWrite(h,"signal_id","setup_time_utc","entry_time_utc","direction","entry","sl","risk",
             "rr","trail_pips","result","r","exit_time_utc","trailing_activated","entry_index","exit_index");

   for(int k=0;k<signals;k++) {
      double r=0; int exit_i=-1; bool active=false;
      string result=ResultForSignal(g_signals[k],r,exit_i,active);
      if(result=="WIN") wins++;
      else if(result=="LOSS") { losses++; streak++; maxstreak=MathMax(maxstreak,streak); }
      else if(result=="BREAKEVEN") { be++; streak=0; }
      else if(result=="AMBIGUOUS") { amb++; streak=0; }
      else { open++; streak=0; }
      if(result=="WIN" || result=="LOSS" || result=="BREAKEVEN") {
         net_r+=r; if(r>0) gp+=r; if(r<0) gl-=r;
         equity+=r; peak=MathMax(peak,equity); maxdd=MathMax(maxdd,peak-equity);
      }
      if(active) trail_count++;

      string sid=IntegerToString(k+1)+"_"+IntegerToString((int)g_signals[k].entry_time)+"_"+g_signals[k].direction;
      string exit_ts=exit_i>=0 ? CsvTime(g_rates[exit_i].time) : "";
      FileWrite(h,sid,CsvTime(g_signals[k].setup_time),CsvTime(g_signals[k].entry_time),
                g_signals[k].direction,DoubleToString(g_signals[k].entry,_Digits),
                DoubleToString(g_signals[k].sl,_Digits),DoubleToString(g_signals[k].risk,_Digits),
                DoubleToString(RR,4),DoubleToString(TRAIL_PIPS,2),result,DoubleToString(r,8),
                exit_ts,active?"1":"0",g_signals[k].entry_index,exit_i);
   }
   FileClose(h);

   int decisive=wins+losses+be;
   double wr=decisive>0 ? 100.0*wins/decisive : 0.0;
   double pf=gl>0 ? gp/gl : 0.0;

   string summary=
      "mode=NON_CANONICAL_FORENSIC\n"+
      "experiment=SP2L_TRAIL10_ONE_YEAR_FIXED_CONTRACT\n"+
      "symbol="+_Symbol+"\n"+
      "requested_start_utc="+CsvTime(start)+"\n"+
      "requested_end_utc="+CsvTime(end)+"\n"+
      "actual_first_bar_utc="+CsvTime(first)+"\n"+
      "actual_last_bar_utc="+CsvTime(last)+"\n"+
      "bars="+IntegerToString(copied)+"\n"+
      "p_gap_price=1.0\nspike_multiplier=1.5\nmax_sl_distance=10.0\nrr=1.0\ntrail_pips=10.0\n"+
      "signals="+IntegerToString(signals)+"\ndecisive="+IntegerToString(decisive)+"\n"+
      "wins="+IntegerToString(wins)+"\nlosses="+IntegerToString(losses)+"\nbreakeven="+IntegerToString(be)+"\n"+
      "ambiguous="+IntegerToString(amb)+"\nopen_or_unresolved="+IntegerToString(open)+"\n"+
      "win_rate_decisive_pct="+DoubleToString(wr,8)+"\nnet_R="+DoubleToString(net_r,8)+"\n"+
      "profit_factor="+DoubleToString(pf,8)+"\nmax_drawdown_R="+DoubleToString(maxdd,8)+"\n"+
      "max_losing_streak="+IntegerToString(maxstreak)+"\ntrailing_activated_count="+IntegerToString(trail_count)+"\n"+
      "volume_lots=0.01\n"+
      "trailing_policy=favorable M1 extreme updates SL for next candle only\n"+
      "same_bar_policy=AMBIGUOUS when active SL and TP both touched\n"+
      "intrabar_order=NOT_INFERRED_FROM_M1_OHLC\n"+
      "canonical=false\n";

   WriteText(summary_txt,summary);
   Print(summary);
   Print("OUTPUT_TRADE_CSV=",trade_csv);
   Print("OUTPUT_SUMMARY=",summary_txt);
   return INIT_SUCCEEDED;
}

void OnTick() {}
void OnDeinit(const int reason) {}
