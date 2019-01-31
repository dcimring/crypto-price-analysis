'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class HigherPriceBacktester(Backtester):
    '''Backtest a strategy that goes long when the price today is higher than lookback
    days ago, and short otherwise

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=7, long_only=False, slippage=0):
        self._lookback = lookback
        super(HigherPriceBacktester,self).__init__(series,long_only=long_only,slippage=slippage)

    def __str__(self):
        return "Higher Price Backtest Strategy (ms=%d, ml=%d, ema=%s, long_only=%s, start=%s, end=%s)" % (
            self._lookback, str(self._long_only), str(self._start_date), str(self._end_date))

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        
        self._df['stance'] = np.where(self._df['last'] >= self._df['last'].shift(self._lookback), 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['last'] < self._df['last'].shift(self._lookback), -1, self._df['stance'])
        

