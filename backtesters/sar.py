'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import talib
from backtester import Backtester

# ToDo - instead of lookback use "current trend" (not yet sure how to calculate this)

class SARBacktester(Backtester):
    '''Backtest a strategy which goes long and short based on parabolic SAR
    See https://www.tradingview.com/wiki/Parabolic_SAR_(SAR)

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    acceleration: (float) determines the sensitivity of the SAR
    maximum: (float) maximum for acceleration
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, high=None, low=None, acceleration=0.02, maximum=0.2, long_only=False):
        self._acceleration = acceleration
        self._maximum = maximum
        super(SARBacktester,self).__init__(series,long_only=long_only)
        if high is not None:
            self._df['high'] = high
        else:
            self._df['high'] = series
        if low is not None:
            self._df['low'] = low
        else:
            self._df['low'] = series

    def __str__(self):
        return "Parabolic SAR Backtest Strategy (acceleration=%0.3f, maximum=%0.3f, long_only=%s, start=%s, end=%s)" % (
            self._acceleration, self._maximum, str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        ax.set_title(self.__str__(), size=13)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['sar'],'.', ms=2, label='sar')
        ax.legend()
        plt.show()


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        #self._df['high'] = self._df['last'].rolling(window=self._lookback).max()  # MAX(close, timeperiod=30)
        #self._df['low'] = self._df['last'].rolling(window=self._lookback).min()  # low = MIN(close, timeperiod=30)

        self._df['sar'] = talib.SAR(self._df['high'], self._df['low'], acceleration=self._acceleration, maximum=self._maximum)

        self._df['stance'] = np.where(self._df['last'] >= self._df['sar'], 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['last'] < self._df['sar'], -1, self._df['stance'])



