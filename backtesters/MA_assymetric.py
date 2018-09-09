'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class MAAssymetricBacktester(Backtester):
    '''Backtest a Moving Average (MA) crossover strategy
    which goes short when pices crosses one MA, and long when
    price cross another

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    short: (int) moving average for going short
    long: (int) moving average for going long
    ema: (boolean) True if you want exponential MA's
    '''

    def __init__(self, series, short_on=7, long_on=4, ema=False):
        self._short_on = short_on
        self._long_on = long_on
        self._ema = ema
        super(MAAssymetricBacktester,self).__init__(series,long_only=False)

    def __str__(self):
        return "MA Assymetric Backtest Strategy (short_on=%d, long_on=%d, ema=%s, long_only=%s, start=%s, end=%s)" % (
            self._short_on, self._long_on, str(self._ema), str(False), str(self._start_date), str(self._end_date))


    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        ax.set_title(self.__str__(), size=13)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['short_on'], label='short_on')
        ax.plot(temp['long_on'], label='long_on')
        ax.legend()
        #plt.show()
        return ax

    def _indicators(self):

        if self._ema:
            self._df['short_on'] = np.round(self._df['last'].ewm(span=self._short_on, adjust=False).mean(),8)
            self._df['long_on'] = np.round(self._df['last'].ewm(span=self._long_on, adjust=False).mean(),8)
        else:
            self._df['short_on'] = np.round(self._df['last'].rolling(window=self._short_on).mean(), 8)
            self._df['long_on'] = np.round(self._df['last'].rolling(window=self._long_on).mean(), 8)

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        # order here is important
        if self._short_on > self._long_on:
            self._df['stance'] = np.where(self._df['last'] <= self._df['short_on'] , -1, 1)
            self._df['stance'] = np.where(self._df['last'] >= self._df['long_on'] , 1, self._df['stance'] )
        else:
            self._df['stance'] = np.where(self._df['last'] >= self._df['long_on'] , 1, -1 )
            self._df['stance'] = np.where(self._df['last'] <= self._df['short_on'] , -1, self._df['stance'] )
            
        

