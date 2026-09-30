//+------------------------------------------------------------------+
//| SP2L V2 MT5 Strategy Tester forensic replica                     |
//| NON_CANONICAL_FORENSIC - research only                           |
//+------------------------------------------------------------------+
#property strict
#property version   "1.0"

// Unix epoch seconds. Using epoch values avoids broker/local timezone parsing.
// 2026-06-28 00:00:00 UTC = 1782604800
// 2026-09-25 00:00:00 UTC = 1790294400
input long     InpStartUnixUTC = 1782604800;
input long     InpEndUnixUTC   = 1790294400;
input double   InpPGAP      = 1.0;
input double   InpSpikeMult = 1.5;
input double   InpMaxSL     = 10.0;
input double   InpRR         = 1.0;
input double   InpTrailPips  = 0.0;   // 0 = OFF; 1 pip = 0.10 XAU price
input double   InpVolumeLots = 0.01;

struct Signal
{
   int      setup_index;
   int      entry_index;
   datetime setup_time;
   datetime entry_time;
   string   direction;
   double   entry;
   double   sl;
   double   risk;
};

MqlRates g_rates[];
Signal   g_signals[];
string   g_prefix = "SP2L_V2_MT5_TESTER";

double Body(const MqlRates &c, const string direction)
{
   if(direction=="BUY")
      return c.close-c.open;
   return c.open-c.close;
}

bool Setup(const int i, const string direction)
{
   if(i<2) return false;
   const MqlRates &before=g_rates[i-2];
   const MqlRates &spike =g_rates[i-1];
   const MqlRates &after =g_rates[i];

   if(direction=="BUY")
      return after.close>spike.close &&
             after.open>spike.open &&
             spike.close>before.close &&
             spike.open>before.open &&
             after.close>after.open &&
             spike.close>spike.open &&
             before.close>before.open &&
             after.low>before.high+InpPGAP &&
             Body(spike,"BUY")>InpSpikeMult*Body(before,"BUY") &&
             Body(spike,"BUY")>InpSpikeMult*Body(after,"BUY");

   return after.close<spike.close &&
          after.open<spike.open &&
          spike.close<before.close &&
          spike.open<before.open &&
          after.close<after.open &&
          spike.close<spike.open &&
          before.close<before.open &&
          after.high<before.low-InpPGAP &&
          Body(spike,"SELL")>InpSpikeMult*Body(before,"SELL") &&
          Body(spike,"SELL")>InpSpikeMult*Body(after,"SELL");
}

bool BuildSignal(const int setup_index, Signal &out)
{
   bool buy=Setup(setup_index,"BUY");
   bool sell=Setup(setup_index,"SELL");
   if(buy==sell) return false;

   string direction=buy ? "BUY" : "SELL";
   double sl=buy ? g_rates[setup_index-2].low : g_rates[setup_index-2].high;

   // Exact Python contract: first qualifying trigger after setup.
   for(int j=setup_index+1;j<ArraySize(g_rates);j++)
   {
      double entry=buy ? g_rates[j].low : g_rates[j].high;
      bool trigger=buy ? entry<g_rates[j-1].low : entry>g_rates[j-1].high;
      if(!trigger) continue;

      double risk=buy ? entry-sl : sl-entry;
      if(risk<=0.0 || risk>InpMaxSL)
         return false;

      out.setup_index=setup_index;
      out.entry_index=j;
      out.setup_time=g_rates[setup_index].time;
      out.entry_time=g_rates[j].time;
      out.direction=direction;
      out.entry=entry;
      out.sl=sl;
      out.risk=risk;
      return true;
   }
   return false;
}

string ResultForSignal(const Signal &s, double &realized_r, int &exit_index, bool &trail_active)
{
   realized_r=0.0;
   exit_index=-1;
   trail_active=false;

   double risk=MathAbs(s.entry-s.sl);
   double tp=(s.direction=="BUY") ? s.entry+InpRR*risk : s.entry-InpRR*risk;
   double current_sl=s.sl;
   double best=s.entry;
   double trail=InpTrailPips*0.10;
   bool trailing_enabled=InpTrailPips>0.0;

   for(int i=s.entry_index;i<ArraySize(g_rates);i++)
   {
      double high=g_rates[i].high;
      double low =g_rates[i].low;

      if(s.direction=="BUY")
      {
         bool sl_hit=low<=current_sl;
         bool tp_hit=high>=tp;

         if(sl_hit && tp_hit)
         {
            exit_index=i;
            return "AMBIGUOUS";
         }
         if(sl_hit)
         {
            realized_r=(current_sl-s.entry)/risk;
            exit_index=i;
            if(realized_r>0.0) return "WIN";
            if(realized_r<0.0) return "LOSS";
            return "BREAKEVEN";
         }
         if(tp_hit)
         {
            realized_r=InpRR;
            exit_index=i;
            return "WIN";
         }

         if(trailing_enabled)
         {
            best=MathMax(best,high);
            if(!trail_active && best>=s.entry+trail)
               trail_active=true;
            if(trail_active)
               current_sl=MathMax(current_sl,best-trail);
         }
      }
      else
      {
         bool sl_hit=high>=current_sl;
         bool tp_hit=low<=tp;

         if(sl_hit && tp_hit)
         {
            exit_index=i;
            return "AMBIGUOUS";
         }
         if(sl_hit)
         {
            realized_r=(s.entry-current_sl)/risk;
            exit_index=i;
            if(realized_r>0.0) return "WIN";
            if(realized_r<0.0) return "LOSS";
            return "BREAKEVEN";
         }
         if(tp_hit)
         {
            realized_r=InpRR;
            exit_index=i;
            return "WIN";
         }

         if(trailing_enabled)
         {
            best=MathMin(best,low);
            if(!trail_active && best<=s.entry-trail)
               trail_active=true;
            if(trail_active)
               current_sl=MathMin(current_sl,best+trail);
         }
      }
   }

   return "OPEN_OR_UNRESOLVED";
}

void WriteText(const string filename,const string text)
{
   int h=FileOpen(filename,FILE_WRITE|FILE_TXT|FILE_ANSI);
   if(h==INVALID_HANDLE)
   {
      Print("FILE_OPEN_FAILED ",filename," err=",GetLastError());
      return;
   }
   FileWriteString(h,text);
   FileClose(h);
}

string CsvEscape(const string s)
{
   string x=s;
   StringReplace(x,"\"","\"\"");
   return "\""+x+"\"";
}

int OnInit()
{
   ArraySetAsSeries(g_rates,false);

   datetime start_utc=(datetime)InpStartUnixUTC;
   datetime end_utc=(datetime)InpEndUnixUTC;
   int copied=CopyRates(_Symbol,PERIOD_M1,start_utc,end_utc,g_rates);
   if(copied<=0)
   {
      Print("COPY_RATES_FAILED err=",GetLastError()," symbol=",_Symbol);
      return INIT_FAILED;
   }
   ArraySetAsSeries(g_rates,false);

   Print("SP2L_TESTER_HISTORY symbol=",_Symbol,
         " bars=",copied,
         " first=",TimeToString(g_rates[0].time,TIME_DATE|TIME_MINUTES),
         " last=",TimeToString(g_rates[copied-1].time,TIME_DATE|TIME_MINUTES));

   ArrayResize(g_signals,0);

   // Same population contract as Python build_population().
   for(int i=2;i<copied;i++)
   {
      Signal s;
      if(BuildSignal(i,s))
      {
         int n=ArraySize(g_signals);
         ArrayResize(g_signals,n+1);
         g_signals[n]=s;
      }
   }

   int signals=ArraySize(g_signals);
   int wins=0,losses=0,be=0,amb=0,open=0,trail_count=0;
   double net_r=0.0,gp=0.0,gl=0.0;
   double equity=0.0,peak=0.0,maxdd=0.0;
   int streak=0,maxstreak=0;

   string stamp=IntegerToString((int)TimeLocal());
   string csv_name=g_prefix+"_trades_"+stamp+".csv";
   string sum_name=g_prefix+"_summary_"+stamp+".txt";

   int h=FileOpen(csv_name,FILE_WRITE|FILE_CSV|FILE_ANSI,',');
   if(h==INVALID_HANDLE)
   {
      Print("TRADE_FILE_OPEN_FAILED err=",GetLastError());
      return INIT_FAILED;
   }

   FileWrite(h,"signal_id","setup_time_utc","entry_time_utc","direction","entry","sl","risk",
             "rr","trail_pips","result","r","exit_time_utc","trailing_activated","entry_index","exit_index");

   for(int k=0;k<signals;k++)
   {
      double r=0.0;
      int exit_i=-1;
      bool active=false;
      string result=ResultForSignal(g_signals[k],r,exit_i,active);

      if(result=="WIN") wins++;
      else if(result=="LOSS") { losses++; streak++; maxstreak=MathMax(maxstreak,streak); }
      else if(result=="BREAKEVEN") { be++; streak=0; }
      else if(result=="AMBIGUOUS") { amb++; streak=0; }
      else { open++; streak=0; }

      if(result=="WIN" || result=="LOSS" || result=="BREAKEVEN")
      {
         net_r+=r;
         if(r>0) gp+=r;
         if(r<0) gl+=-r;
         equity+=r;
         peak=MathMax(peak,equity);
         maxdd=MathMax(maxdd,peak-equity);
      }

      if(active) trail_count++;

      string sid=IntegerToString(k+1)+"_"+IntegerToString((int)g_signals[k].entry_time)+"_"+g_signals[k].direction;
      string setup_ts=TimeToString(g_signals[k].setup_time,TIME_DATE|TIME_MINUTES|TIME_SECONDS);
      string entry_ts=TimeToString(g_signals[k].entry_time,TIME_DATE|TIME_MINUTES|TIME_SECONDS);
      string exit_ts=(exit_i>=0 ? TimeToString(g_rates[exit_i].time,TIME_DATE|TIME_MINUTES|TIME_SECONDS) : "");

      FileWrite(h,sid,setup_ts,entry_ts,g_signals[k].direction,
                DoubleToString(g_signals[k].entry,_Digits),
                DoubleToString(g_signals[k].sl,_Digits),
                DoubleToString(g_signals[k].risk,_Digits),
                DoubleToString(InpRR,4),DoubleToString(InpTrailPips,2),
                result,DoubleToString(r,8),exit_ts,
                active ? "1":"0",g_signals[k].entry_index,exit_i);
   }
   FileClose(h);

   int decisive=wins+losses+be;
   double wr=(decisive>0 ? 100.0*wins/decisive : 0.0);
   double pf=(gl>0.0 ? gp/gl : 0.0);
   double contract=SymbolInfoDouble(_Symbol,SYMBOL_TRADE_CONTRACT_SIZE);
   double net_usd=net_r*InpVolumeLots*contract; // R*price-risk is NOT constant; USD is recomputed below.

   // Recompute USD exactly per trade risk * R.
   double usd_net=0.0,usd_gp=0.0,usd_gl=0.0,usd_avg_risk=0.0;
   for(int k=0;k<signals;k++)
   {
      double r=0.0; int exit_i=-1; bool active=false;
      string result=ResultForSignal(g_signals[k],r,exit_i,active);
      usd_avg_risk += g_signals[k].risk*contract*InpVolumeLots;
      if(result=="WIN" || result=="LOSS" || result=="BREAKEVEN")
      {
         double pnl=r*g_signals[k].risk*contract*InpVolumeLots;
         usd_net+=pnl;
         if(pnl>0) usd_gp+=pnl;
         if(pnl<0) usd_gl-=pnl;
      }
   }
   if(signals>0) usd_avg_risk/=signals;

   string summary=
      "mode=NON_CANONICAL_FORENSIC\n"+
      "experiment=SP2L_V2_MT5_STRATEGY_TESTER_REPLICA\n"+
      "symbol="+_Symbol+"\n"+
      "start_utc="+TimeToString(start_utc,TIME_DATE|TIME_MINUTES)+"\n"+
      "end_utc="+TimeToString(end_utc,TIME_DATE|TIME_MINUTES)+"\n"+
      "bars="+IntegerToString(copied)+"\n"+
      "signals="+IntegerToString(signals)+"\n"+
      "decisive="+IntegerToString(decisive)+"\n"+
      "wins="+IntegerToString(wins)+"\n"+
      "losses="+IntegerToString(losses)+"\n"+
      "breakeven="+IntegerToString(be)+"\n"+
      "ambiguous="+IntegerToString(amb)+"\n"+
      "open_or_unresolved="+IntegerToString(open)+"\n"+
      "win_rate_decisive_pct="+DoubleToString(wr,8)+"\n"+
      "net_R="+DoubleToString(net_r,8)+"\n"+
      "profit_factor="+DoubleToString(pf,8)+"\n"+
      "max_drawdown_R="+DoubleToString(maxdd,8)+"\n"+
      "max_losing_streak="+IntegerToString(maxstreak)+"\n"+
      "trailing_activated_count="+IntegerToString(trail_count)+"\n"+
      "net_usd="+DoubleToString(usd_net,8)+"\n"+
      "gross_profit_usd="+DoubleToString(usd_gp,8)+"\n"+
      "gross_loss_usd="+DoubleToString(usd_gl,8)+"\n"+
      "average_initial_risk_usd="+DoubleToString(usd_avg_risk,8)+"\n"+
      "contract_size="+DoubleToString(contract,4)+"\n"+
      "volume_lots="+DoubleToString(InpVolumeLots,4)+"\n"+
      "p_gap_price="+DoubleToString(InpPGAP,4)+"\n"+
      "spike_multiplier="+DoubleToString(InpSpikeMult,4)+"\n"+
      "max_sl_distance="+DoubleToString(InpMaxSL,4)+"\n"+
      "rr="+DoubleToString(InpRR,4)+"\n"+
      "trail_pips="+DoubleToString(InpTrailPips,4)+"\n"+
      "trail_zero_semantics=OFF\n"+
      "trailing_policy=favorable M1 extreme updates SL for next candle only\n"+
      "same_bar_policy=AMBIGUOUS when active SL and TP both touched\n"+
      "intrabar_order=NOT_INFERRED_FROM_M1_OHLC\n"+
      "canonical=false\n";

   WriteText(sum_name,summary);
   Print(summary);
   Print("OUTPUT_CSV=",csv_name);
   Print("OUTPUT_SUMMARY=",sum_name);

   return INIT_SUCCEEDED;
}

void OnTick()
{
   // Research calculation is performed once in OnInit().
}

void OnDeinit(const int reason)
{
   // No trading and no persistent terminal state.
}
