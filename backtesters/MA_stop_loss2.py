'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from MA_stop_loss import MAStopLossBacktester
from IPython.core.debugger import set_trace

class MAStopLossBacktester2(MAStopLossBacktester):
    '''Backtest a Moving Average (MA) crossover strategy with stop loss for BOTH the shorts and the long sides
    To test a strategy that holds physical and only shorts using futures use MAStopLossBacktester

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    ml: (int) long moving average
    ema: (boolean) True if you want exponential MA's
    stop_loss: (float) stop loss for shorts only eg 0.05 means a 5% stop loss
    trailing_stop (boolean) True if you want to use trailing stops
    EOD_only (boolean) True if you make trades only at end of day
    '''

    def __init__(self, series, highs=None, lows=None, ms=1, ml=10, ema=False, stop_loss = 0.05, trailing_stop=False, EOD_only=True, slippage=0):
        
        super(MAStopLossBacktester2,self).__init__(series,highs=highs, lows=lows, ms=ms,ml=ml,ema=ema, stop_loss=stop_loss, trailing_stop=trailing_stop, EOD_only=EOD_only, slippage=slippage)


    def __str__(self):
        return "MA Stop Loss Backtest Strategy 2 (ms=%d, ml=%d, ema=%s, long_only=%s, stop=%0.3f, trailing_stop=%s, EOD_only=%s, freq='%s', start=%s, end=%s)" % (
            self._ms, self._ml, str(self._ema), str(self._long_only), self._stop_loss,
            str(self._trailing_stop), str(self._EOD_only), self._freq, str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = MABacktester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['stop_short'],color='orange', linestyle='None', marker='o')
        ax.plot(temp['stop_long'],color='orange', linestyle='None', marker='o')
        ax.legend()
        plt.show()

    
    def _market_returns(self):
        
        # Override this method so that stop loss trade prices can be adjusted for
        self._df['last_adj_stops'] = np.where(~self._df['stop_short'].isnull(),self._df['stop_short'],self._df['last'])
        self._df['last_adj_stops'] = np.where(~self._df['stop_long'].isnull(),self._df['stop_long'],self._df['last'])
        self._df['market'] = np.log(self._df['last_adj_stops'] / self._df['last_adj_stops'].shift(1))
        self._df['buy'] = np.where( self._df['stance'] - self._df['stance'].shift(1).fillna(0) > 0, self._df['last_adj_stops'], np.NAN)
        self._df['sell'] = np.where( self._df['stance'] - self._df['stance'].shift(1).fillna(0) < 0, self._df['last_adj_stops'], np.NAN)

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()

        # If I hit a stop loss can I go long the same day? Yes in fact check for go long first in which case stop not needed
        # If a short gets stopped out then wait for next buy before any more shorts

        current_stance = 0
        stances = []
        entry_price = None
        current_price = None
        stop_loss = None
        
        # list of stops to be used for chart
        stop_short = stop_long = self._df['last'].copy()
        stop_short[:] = stop_long[:] = np.nan 
        
        wait_for_long = wait_for_short = False
        #stop_loss = self._stop_loss

        for index, row in self._df.iterrows():
            
            # Handle intraday data and also support EOD only trades

            if index.hour == 0:
                end_of_day = True
            else:
                end_of_day = False

            current_price = row['last']
            current_high = row['high']
            current_low = row['low']
            
            buy_signal = False
            sell_signal = False
            

            # Check for stop loss

            if current_stance == -1: 

                if self._trailing_stop:
                    if current_low < entry_price:
                        stop_price = current_low + stop_loss

                if current_high >= stop_price: 
                    current_stance = 0 # if short is stopped then you are flat
                    stop_short.loc[index] = current_high
                    print "Stop loss for short triggered at %s entry %0.5f exit %0.5f loss %0.1f%%" % (str(index),
                        entry_price, current_high, (entry_price/current_high-1) * 100)
                    entry_price = None
                    wait_for_long = True # If a short gets stopped out then wait for next long before shorting again
            
            elif current_stance == 1: 

                if self._trailing_stop:
                    if current_high > entry_price:
                        stop_price = current_high - stop_loss

                if current_low <= stop_price: 
                    current_stance = 0 # if short is stopped then you are now flat
                    stop_long.loc[index] = current_low
                    print "Stop loss for long triggered at %s entry %0.5f exit %0.5f loss %0.1f%%" % (str(index),
                        entry_price, current_low, (current_low/entry_price-1) * 100)
                    entry_price = None
                    wait_for_short = True # If a long gets stopped out then wait for next short before going long again

            if end_of_day or not self._EOD_only:

                if row['mdiff'] >= 0:
                    buy_signal = True
                if row['mdiff'] < 0 :
                    sell_signal = True

                if current_stance == 0:
                    if buy_signal and not wait_for_short:
                        current_stance = 1
                        entry_price = current_price
                        stop_loss = self._stop_loss * entry_price
                        stop_price = current_price - stop_loss
                        wait_for_long = False
                    if sell_signal and not wait_for_long:
                        current_stance = -1
                        entry_price = current_price
                        stop_loss = self._stop_loss * entry_price
                        stop_price = current_price + stop_loss
                        wait_for_short = False
                        #print "Going short on %s at %0.1f" % (str(index),entry_price)
                elif current_stance == 1 and not wait_for_long:
                    if sell_signal:
                        wait_for_short = False
                        current_stance = -1
                        entry_price = current_price
                        stop_loss = self._stop_loss * entry_price
                        stop_price = current_price + stop_loss
                        #print "Going short on %s at %0.1f" % (str(index),entry_price)
                else: # you are -1
                    if buy_signal and not wait_for_short:
                        current_stance = 1
                        entry_price = current_price
                        stop_loss = self._stop_loss * entry_price
                        stop_price = current_price - stop_loss
                        wait_for_long = False

            
            stances.append(current_stance)

        self._df['stance'] = stances
        self._df['stop_short'] = stop_short
        self._df['stop_long'] = stop_long




