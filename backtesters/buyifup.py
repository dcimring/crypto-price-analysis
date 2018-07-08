'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class BuyIfUpBacktester(Backtester):
    '''Backtest a strategy where you are long if the price today is higher 
    than lookback days ago, in cash or short if lower

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=1, long_only=False):
        self._lookback = lookback
        super(BuyIfUpBacktester,self).__init__(series,long_only=long_only)
            

    def __str__(self):
        return "BuyIfUp Backtest Strategy (lookback=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, str(self._long_only), str(self._start_date), str(self._end_date))


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._df['stance'] = np.where(self._df['last'] >= self._df['last'].shift(self._lookback), 1,0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['last'] < self._df['last'].shift(self._lookback),-1, self._df['stance'])
        

