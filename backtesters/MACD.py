'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class MACDBacktester(Backtester):
    '''Backtest a RSI strategy

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    fast: (int) lookback period for fast ema
    slow: (int) lookback period for slow ema
    signal: (int) lookback for signal smoothing
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, fast=12, slow=26, signal=9, long_only=False):
        self._fast=fast
        self._slow=slow
        self._signal=signal
        Backtester.__init__(self,series,long_only=long_only)

    def __str__(self):
        return "MACD Backtest Strategy (fast=%d, slow=%d, signal=%d, long_only=%s, start=%s, end=%s)" % (
            self._fast, self._slow, self._signal, str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("dark")
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=figsize, gridspec_kw = {'height_ratios':[3, 1]})
        fig.suptitle(self.__str__(), size=13)

        Backtester.plot(self,start_date=start_date,end_date=end_date, ax=ax1)
        temp = self._df.loc[start_date:end_date]
        ax1.legend()
        
        ax2.plot(temp['MACD'])
        ax2.plot(temp['signal'])
        
        plt.tight_layout()
        plt.show()

    def _MACD(self):
        '''Calculate the MACD'''
        self._df['slow'] = self._df['last'].ewm(span=self._slow).mean()
        self._df['fast'] = self._df['last'].ewm(span=self._fast).mean()
        self._df['MACD'] = self._df['fast'] - self._df['slow']
        self._df['signal'] = self._df['MACD'].rolling(window=self._signal).mean()

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._MACD()

        self._df['mdiff'] = self._df['MACD'] - self._df['signal']
        self._df['stance'] = np.where(self._df['mdiff'] >= 0, 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['mdiff'] < 0, -1, self._df['stance'])
        


