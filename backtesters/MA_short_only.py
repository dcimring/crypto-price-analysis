'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from MA import MABacktester

class MAShortOnlyBacktester(MABacktester):
    '''Backtest a Moving Average (MA) crossover strategy that only goes short

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    ml: (int) long moving average
    ema: (boolean) True if you want exponential MA's
    '''

    def __init__(self, series, ms=1, ml=10, ema=False):
        self._ms = ms
        self._ml = ml
        self._ema = ema
        super(MAShortOnlyBacktester,self).__init__(series,ms=ms,ml=ml,long_only=False,ema=ema)

    def __str__(self):
        return "MA Short Only Backtest Strategy (ms=%d, ml=%d, ema=%s, start=%s, end=%s)" % (
            self._ms, self._ml, str(self._ema), str(self._start_date), str(self._end_date))

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        self._df['stance'] = np.where(self._df['mdiff'] < 0, -1, 0)
        

