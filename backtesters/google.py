'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class GoogleBacktester(Backtester):
    '''Backtest a strategy that uses bitcoin searches on google
    for signals

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    searches (Panda Series) a list of google search volume by date
    ms: (int) short moving average
    ml: (int) long moving average
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, searches, ms=1, ml=10, long_only=False):
        self._ms = ms
        self._ml = ml
        super(GoogleBacktester,self).__init__(series,long_only=long_only)
        self._df['searches'] = searches

    def __str__(self):
        return "Google Searches Backtest Strategy (ms=%d, ml=%d, long_only=%s, start=%s, end=%s)" % (
            self._ms, self._ml, str(self._long_only), str(self._start_date), str(self._end_date))


    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        ax.set_title(self.__str__(), size=13)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['ml'], label='ml')
        if self._ms > 1:
            ax.plot(temp['ms'], label='ms')
        ax.legend()
        #plt.show()
        return ax

    def _indicators(self):

        self._df['ms'] = np.round(self._df['searches'].rolling(window=self._ms).mean(), 8)
        self._df['ml'] = np.round(self._df['searches'].rolling(window=self._ml).mean(), 8)

        self._df['mdiff'] = self._df['ms'] - self._df['ml']

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        self._df['stance'] = np.where(self._df['mdiff'] >= 0, 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['mdiff'] < 0, -1, self._df['stance'])
        

