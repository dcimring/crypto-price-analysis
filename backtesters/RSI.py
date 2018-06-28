'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class RSIBacktester(Backtester):
    '''Backtest a RSI strategy

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=14, buy_on=70, sell_on=30, long_only=False):
        self._lookback=lookback
        self._buy_on=buy_on
        self._sell_on=sell_on
        Backtester.__init__(self,series,long_only=long_only)

    def __str__(self):
        return "RSI Backtest Strategy (lookback=%d, buy_on=%d, sell_on=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, self._buy_on, self._sell_on, str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("dark")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        temp = self._df.loc[start_date:end_date]
        plt.legend()
        plt.show()
        #plt.subplot(212, sharex=ax)
        temp['RSI'].plot(figsize=(figsize[0],4))
        plt.hlines(self._buy_on,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        plt.hlines(self._sell_on,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        #plt.plot(temp['RSI'])
        plt.show()

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        delta = self._df['last'].diff()
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        RolUp = dUp.rolling(window=self._lookback).mean()
        RolDown = dDown.abs().rolling(window=self._lookback).mean()

        RS = RolUp / RolDown
        RSI = 100.0 - (100.0 / (1.0 + RS))
        self._df['RSI'] = RSI

        # long when RSI is high, short when it is low, in cash otherwise
        # there are other strategies
        # https://tradingsim.com/blog/rsi-relative-strength-index/

        self._df['stance'] = np.where(self._df['RSI'] >= self._buy_on, 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['RSI'] <= self._sell_on, -1, self._df['stance'])


