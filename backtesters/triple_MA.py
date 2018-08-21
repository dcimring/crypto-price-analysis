'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class TripleMABacktester(Backtester):
    '''Backtest a Moving Average (MA) crossover strategy which has 3 MA's

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    mi: (int) intermediate moving average
    ml: (int) long moving average
    long_only: (boolean) True if the strategy can only go long
    ema: (boolean) True if you want exponential MA's
    '''

    def __init__(self, series, ms=1, mi=7, ml=20, long_only=False, ema=False):
        self._ms = ms
        self._mi = mi
        self._ml = ml
        self._ema = ema
        super(TripleMABacktester,self).__init__(series,long_only=long_only)

    def __str__(self):
        return "Triple MA Backtest Strategy (ms=%d, mi=%d, ml=%d, ema=%s, long_only=%s, start=%s, end=%s)" % (
            self._ms, self._mi, self._ml, str(self._ema), str(self._long_only), str(self._start_date), str(self._end_date))


    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        ax.set_title(self.__str__(), size=13)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['mi'], label='mi')
        ax.plot(temp['ml'], label='ml')
        if self._ms > 1:
            ax.plot(temp['ms'], label='ms')
        ax.legend()
        #plt.show()
        return ax

    def _indicators(self):

        if self._ema:
            self._df['ms'] = np.round(self._df['last'].ewm(span=self._ms, adjust=False).mean(),8)
            self._df['mi'] = np.round(self._df['last'].ewm(span=self._mi, adjust=False).mean(),8)
            self._df['ml'] = np.round(self._df['last'].ewm(span=self._ml, adjust=False).mean(),8)
        else:
            self._df['ms'] = np.round(self._df['last'].rolling(window=self._ms).mean(), 8)
            self._df['mi'] = np.round(self._df['last'].rolling(window=self._mi).mean(), 8)
            self._df['ml'] = np.round(self._df['last'].rolling(window=self._ml).mean(), 8)


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        self._df['stance'] = np.where( (self._df['ms'] >= self._df['mi']) & (self._df['mi'] > self._df['ml']), 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where( (self._df['ms'] <= self._df['mi']) & (self._df['mi'] <= self._df['ml']), -1, self._df['stance'])
        

