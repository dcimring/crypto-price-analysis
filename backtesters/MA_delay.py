'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from MA import MABacktester

class MADelayBacktester(MABacktester):
    '''Backtest a Moving Average (MA) crossover strategy
    When you get a signal you wait one more day to see if the signal
    is confirmed.

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    ml: (int) long moving average
    long_only: (boolean) True if the strategy can only go long
    ema: (boolean) True if you want exponential MA's
    '''

    def __init__(self, series, ms=1, ml=10, long_only=False, ema=False):
        super(MADelayBacktester,self).__init__(series,ms=ms, ml=ml, long_only=long_only, ema=ema)

    def __str__(self):
        return "MA Delay Backtest Strategy (ms=%d, ml=%d, ema=%s, long_only=%s, start=%s, end=%s)" % (
            self._ms, self._ml, str(self._ema), str(self._long_only), str(self._start_date), str(self._end_date))


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        self._df['stance'] = np.where( (self._df['mdiff'] >= 0) & (self._df['mdiff'].shift(1) >= 0), 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where( (self._df['mdiff'] >= 0) & (self._df['mdiff'].shift(1) >= 0), 1, -1)
        

