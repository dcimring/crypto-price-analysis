'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from MA import MABacktester

class MAStopLossBacktester(MABacktester):
    '''Backtest a Moving Average (MA) crossover strategy with stop loss for the shorts

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    ml: (int) long moving average
    long_only: (boolean) True if the strategy can only go long
    ema: (boolean) True if you want exponential MA's
    stop_loss: (float) stop loss for shorts only eg 0.05 means a 5% stop loss
    '''

    def __init__(self, series, ms=1, ml=10, long_only=False, ema=False, stop_loss = 0.05):
        self._stop_loss = stop_loss
        super(MAStopLossBacktester,self).__init__(series,ms=ms,ml=ml,long_only=long_only,ema=ema)

    def __str__(self):
        return "MA Stop Loss Backtest Strategy (ms=%d, ml=%d, ema=%s, long_only=%s, stop=%0.3f, start=%s, end=%s)" % (
            self._ms, self._ml, str(self._ema), str(self._long_only), self._stop_loss, str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = MABacktester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['stop'],color='orange', linestyle='None', marker='o')
        ax.legend()
        plt.show()

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
        stops = self._df['last'].copy()
        stops[:] = np.nan
        wait_for_long = False 

        for index, row in self._df.iterrows():
            
            current_price = row['last']
            buy_signal = False
            sell_signal = False
            
            if row['mdiff'] >= 0:
                buy_signal = True
            if row['mdiff'] < 0:
                sell_signal = True

            if current_stance == 0:
                if buy_signal:
                    current_stance = 1
                    entry_price = current_price
                    wait_for_long = False
                if sell_signal and not self._long_only and not wait_for_long:
                    current_stance = -1
                    entry_price = current_price
                    #print "Going short on %s at %0.1f" % (str(index),entry_price)
            elif current_stance == 1:
                if sell_signal:
                    current_stance = 0
                    entry_price = None
                    if not self._long_only and not wait_for_long:
                        current_stance = -1
                        entry_price = current_price
                        #print "Going short on %s at %0.1f" % (str(index),entry_price)
            else:
                if buy_signal:
                    current_stance = 1
                    entry_price = current_price
                    wait_for_long = False

            # Check for stop loss
            # If we went long above and stop would have trigered today then fine stop was not needed
             
            if current_stance == -1:
                if entry_price / current_price <= (1-self._stop_loss):
                    current_stance = 0 # go to cash
                    #stances.append(current_stance)
                    stops.loc[index] = current_price
                    print "Stop loss triggered at %s entry %0.2f exit %0.2f loss %0.1f%%" % (str(index),
                        entry_price, current_price, (entry_price/current_price-1) * 100)
                    entry_price = None
                    wait_for_long = True # If a short gets stopped out then wait for next buy before shorting again
            
            stances.append(current_stance)

        self._df['stance'] = stances
        self._df['stop'] = stops


