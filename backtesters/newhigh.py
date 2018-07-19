'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class NewHighBacktester(Backtester):
    '''Backtest a strategy where you are long if the price today is a new 
    high over the lookback period, or within tolerance of a high

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=7, tolerance=0.05, long_only=False):
        self._lookback = lookback
        self._tolerance = tolerance
        super(NewHighBacktester,self).__init__(series,long_only=long_only)
            

    def __str__(self):
        return "NewHigh Backtest Strategy (lookback=%d, tolerance =%0.4f, long_only=%s, start=%s, end=%s)" % (
            self._lookback, self._tolerance, str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        ax.set_title(self.__str__(), size=13)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['max'] * (1-self._tolerance), label='high')
        ax.legend()
        plt.show()


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._df['max'] = self._df['last'].rolling(window=self._lookback).max()

        self._df['stance'] = np.where(self._df['last'] >= self._df['max'] * (1-self._tolerance),1,0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['last'] < self._df['max'] * (1-self._tolerance), -1, self._df['stance'])



