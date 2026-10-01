#property strict
#property version "3.0"
#include <Trade/Trade.mqh>

CTrade trade;

input double InpVolume=0.01;
input double InpPGap=1.0;
input double InpSpikeMultiplier=1.5;
input double InpMaxSLDistance=10.0;
input double InpTPR=1.0;
input double InpTrailPips=10.0;
input int    InpPendingTTLMinutes=30;
input long   InpMagic=26092331;

const string VERSION_ID="SP2L_V3_XAUUSD_TRAIL10_20261001";
const double XAU_PIP_PRICE=0.10;

datetime last_bar=0;
datetime last_signal_time=0;
int journal=INVALID_HANDLE;

double N(double p){ return NormalizeDouble(p,(int)SymbolInfoInteger(_Symbol,SYMBOL_DIGITS)); }

void LogRow(string event_name, string direction="", datetime t=0,
            double entry=0,double sl=0,double tp=0,double exit_price=0,
            double r=0,string reason="",string detail="")
{
   if(journal==INVALID_HANDLE) return;
   FileWrite(journal,TimeToString(TimeCurrent(),TIME_DATE|TIME_SECONDS),
             VERSION_ID,event_name,direction,(long)t,
             DoubleToString(entry,_Digits),DoubleToString(sl,_Digits),
             DoubleToString(tp,_Digits),DoubleToString(exit_price,_Digits),
             DoubleToString(r,4),reason,detail);
   FileFlush(journal);
}

bool SetupOK(MqlRates &before,MqlRates &spike,MqlRates &after,bool &buy,bool &sell)
{
   double bb=MathAbs(before.close-before.open);
   double sb=MathAbs(spike.close-spike.open);
   double ab=MathAbs(after.close-after.open);
   buy=(after.close>spike.close && after.open>spike.open &&
        spike.close>before.close && spike.open>before.open &&
        after.close>after.open && spike.close>spike.open &&
        before.close>before.open &&
        after.low>before.high+InpPGap &&
        sb>InpSpikeMultiplier*bb && sb>InpSpikeMultiplier*ab);
   sell=(after.close<spike.close && after.open<spike.open &&
         spike.close<before.close && spike.open<before.open &&
         after.close<after.open && spike.close<spike.open &&
         before.close<before.open &&
         after.high<before.low-InpPGap &&
         sb>InpSpikeMultiplier*bb && sb>InpSpikeMultiplier*ab);
   return buy||sell;
}

bool FindCurrentTrigger(MqlRates &bars[],int n,
                        bool &is_buy,datetime &trigger_time,
                        double &entry,double &sl,double &tp)
{
   if(n<8) return false;
   // bars[] is series: 0 forming, 1 latest completed. We only create a
   // signal when the just-completed bar is the first valid later trigger.
   int trigger_idx=1;
   for(int k=2;k<n-3;k++)
   {
      MqlRates after=bars[k], spike=bars[k+1], before=bars[k+2];
      bool buy=false,sell=false;
      if(!SetupOK(before,spike,after,buy,sell)) continue;

      bool found=false; int first_idx=-1;
      for(int j=k-1;j>=trigger_idx;j--)
      {
         if(buy && bars[j].low<bars[j+1].low){found=true;first_idx=j;break;}
         if(sell && bars[j].high>bars[j+1].high){found=true;first_idx=j;break;}
      }
      if(!found || first_idx!=trigger_idx) continue;

      double e=buy?bars[trigger_idx].low:bars[trigger_idx].high;
      double s=buy?before.low:before.high;
      double risk=buy?e-s:s-e;
      if(risk<=0 || risk>InpMaxSLDistance) continue;
      is_buy=buy; trigger_time=bars[trigger_idx].time; entry=e; sl=s;
      tp=buy?e+InpTPR*risk:e-InpTPR*risk;
      return true;
   }
   return false;
}

void PlaceSignal()
{
   MqlRates bars[];
   ArraySetAsSeries(bars,true);
   int n=CopyRates(_Symbol,PERIOD_M1,0,300,bars);
   if(n<8) return;

   bool buy=false; datetime tt=0; double entry=0,sl=0,tp=0;
   if(!FindCurrentTrigger(bars,n,buy,tt,entry,sl,tp)) return;
   if(tt==last_signal_time) return;
   last_signal_time=tt;

   double risk=MathAbs(entry-sl);
   string dir=buy?"BUY":"SELL";
   LogRow("SIGNAL",dir,tt,entry,sl,tp,0,0,"",StringFormat("risk=%.2f trail=%.1f pip",risk,InpTrailPips));

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetTypeFillingBySymbol(_Symbol);
   datetime expiration=TimeCurrent()+InpPendingTTLMinutes*60;
   bool ok=false;
   if(buy) ok=trade.BuyLimit(InpVolume,N(entry),_Symbol,N(sl),N(tp),ORDER_TIME_SPECIFIED,expiration,"SP2L_V3_TRAIL10");
   else    ok=trade.SellLimit(InpVolume,N(entry),_Symbol,N(sl),N(tp),ORDER_TIME_SPECIFIED,expiration,"SP2L_V3_TRAIL10");

   LogRow("ORDER_RESULT",dir,tt,entry,sl,tp,0,0,
          ok?"PLACED":"REJECTED",
          trade.ResultRetcodeDescription());
}

void TrailCompletedBar()
{
   MqlRates b[];
   ArraySetAsSeries(b,true);
   if(CopyRates(_Symbol,PERIOD_M1,1,1,b)!=1) return;

   double trail=InpTrailPips*XAU_PIP_PRICE;
   for(int i=PositionsTotal()-1;i>=0;i--)
   {
      ulong ticket=PositionGetTicket(i);
      if(ticket==0 || !PositionSelectByTicket(ticket)) continue;
      if(PositionGetString(POSITION_SYMBOL)!=_Symbol) continue;
      if((long)PositionGetInteger(POSITION_MAGIC)!=InpMagic) continue;

      long type=PositionGetInteger(POSITION_TYPE);
      double entry=PositionGetDouble(POSITION_PRICE_OPEN);
      double old_sl=PositionGetDouble(POSITION_SL);
      double tp=PositionGetDouble(POSITION_TP);
      double new_sl=0;
      bool update=false;

      if(type==POSITION_TYPE_BUY && b[0].high-entry>=trail)
      {
         new_sl=N(b[0].high-trail);
         if(new_sl>old_sl && new_sl<b[0].high) update=true;
      }
      if(type==POSITION_TYPE_SELL && entry-b[0].low>=trail)
      {
         new_sl=N(b[0].low+trail);
         if((old_sl==0 || new_sl<old_sl) && new_sl>b[0].low) update=true;
      }
      if(!update) continue;

      bool ok=trade.PositionModify(ticket,new_sl,tp);
      LogRow("TRAIL_UPDATE",type==POSITION_TYPE_BUY?"BUY":"SELL",b[0].time,
             entry,new_sl,tp,0,0,ok?"UPDATED":"REJECTED",
             StringFormat("bar_high=%.2f bar_low=%.2f ret=%s",b[0].high,b[0].low,trade.ResultRetcodeDescription()));
   }
}

int OnInit()
{
   journal=FileOpen("SP2L_V3_XAUUSD_TRAIL10_MT5_JOURNAL.csv",
                    FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_SHARE_READ|FILE_SHARE_WRITE);
   if(journal==INVALID_HANDLE) return INIT_FAILED;
   FileWrite(journal,"ts","version","event","direction","event_time","entry","sl","tp","exit","r","reason","detail");
   trade.SetExpertMagicNumber(InpMagic);
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   if(journal!=INVALID_HANDLE) FileClose(journal);
}

void OnTick()
{
   datetime bar=iTime(_Symbol,PERIOD_M1,0);
   if(bar==0 || bar==last_bar) return;
   last_bar=bar;
   TrailCompletedBar();
   PlaceSignal();
}

void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
   if(trans.deal==0 || !HistoryDealSelect(trans.deal)) return;
   long magic=HistoryDealGetInteger(trans.deal,DEAL_MAGIC);
   if(magic!=InpMagic) return;
   long entry_type=HistoryDealGetInteger(trans.deal,DEAL_ENTRY);
   double price=HistoryDealGetDouble(trans.deal,DEAL_PRICE);
   double profit=HistoryDealGetDouble(trans.deal,DEAL_PROFIT);
   double swap=HistoryDealGetDouble(trans.deal,DEAL_SWAP);
   double commission=HistoryDealGetDouble(trans.deal,DEAL_COMMISSION);
   string reason=EnumToString((ENUM_DEAL_REASON)HistoryDealGetInteger(trans.deal,DEAL_REASON));
   LogRow(entry_type==DEAL_ENTRY_IN?"FILL":"CLOSE","",TimeCurrent(),price,0,0,price,0,
          reason,StringFormat("deal=%I64u net=%.2f",trans.deal,profit+swap+commission));
}
