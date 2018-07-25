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

        for index, row in self._df.iterrows():
            buy_signal = False
            sell_signal = False
            if row['mdiff'] >= 0:
                buy_signal = True
            if row['mdiff'] < 0:
                sell_signal = True

            if current_stance == 0:
                if buy_signal:
                    current_stance = 1
                if sell_signal and not self._long_only:
                    current_stance = -1
            elif current_stance == 1:
                if sell_signal:
                    current_stance = 0
                    if not self._long_only:
                        current_stance = -1
            else:
                if buy_signal: current_stance = 1
            stances.append(current_stance)

        self._df['stance'] = stances

