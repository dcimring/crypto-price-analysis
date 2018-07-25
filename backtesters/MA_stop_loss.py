'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from MA import MABacktester

class MAStopLossBacktester(MABacktester):
    '''Backtest a Moving Average (MA) crossover strategy

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    ml: (int) long moving average
    long_only: (boolean) True if the strategy can only go long
    ema: (boolean) True if you want exponential MA's
    '''

    def __init__(self, series, ms=1, ml=10, long_only=False, ema=False):
        super(MAStopLossBacktester,self).__init__(series,ms=ms,ml=ml,long_only=long_only,ema=ema)

    def __str__(self):
        return "MA Stop Loss Backtest Strategy (ms=%d, ml=%d, ema=%s, long_only=%s, start=%s, end=%s)" % (
            self._ms, self._ml, str(self._ema), str(self._long_only), str(self._start_date), str(self._end_date))

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        current_stance = 0
        stances = []
        entry_price = None
        current_price = None

        for index, row in self._df.iterrows():
            
            current_price = row['last']
            buy_signal = False
            sell_signal = False
            
            # Check for stop loss
            if current_stance == -1:
                if current_price / entry_price <= (1-0.05):
                    current_stance = 0 # go to cash
                    stances.append(current_stance)
                    print "Stop loss triggered at %s entry %0.1f exit %0.1f loss %0.1f%%" % (str(index), entry_price, current_price, (current_price/entry_price-1) * 100)
                    entry_price = None
                    continue

            if row['mdiff'] >= 0:
                buy_signal = True
            if row['mdiff'] < 0:
                sell_signal = True

            if current_stance == 0:
                if buy_signal:
                    current_stance = 1
                    entry_price = current_price
                if sell_signal and not self._long_only:
                    current_stance = -1
                    entry_price = current_price
                    #print "Going short on %s at %0.1f" % (str(index),entry_price)
            elif current_stance == 1:
                if sell_signal:
                    current_stance = 0
                    entry_price = None
                    if not self._long_only:
                        current_stance = -1
                        entry_price = current_price
                        #print "Going short on %s at %0.1f" % (str(index),entry_price)
            else:
                if buy_signal:
                    current_stance = 1
                    entry_price = current_price
            
            stances.append(current_stance)

        self._df['stance'] = stances

