'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class VWAPBacktester(Backtester):
    '''Backtest a strategy that uses rolling VWAP (volume weighted average price)

    VWAP = Cumulative(Typical Price x Volume) / Cumulative(Volume)

    By using a rolling period this is effectively a MA that weights price by volume

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    volume: (Panda Series) a list of VOLUME by date
    lookback: (int) Lookback for rolling VWAP
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, volume, lookback=7, long_only=False):
        super(VWAPBacktester,self).__init__(series,long_only=long_only)
        self._df['volume'] = volume
        self._lookback = lookback

    def __str__(self):
        return "VWAP Backtest Strategy (long_only=%s, start=%s, end=%s)" % (
            str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("white")
        ax = Backtester.plot(self,start_date=start_date,end_date=end_date,figsize=figsize)
        ax.set_title(self.__str__(), size=13)
        temp = self._df.loc[start_date:end_date]
        ax.plot(temp['vwap'], label='vwap')
        ax.legend()
        #plt.show()
        return ax

    def _indicators(self):

        self._df['cum_vol'] = self._df['volume'].rolling(window=self._lookback).sum()
        #self._df['cum_vol_price'] = (self._df['volume'] * (self._df['high'] + self._df['low'] + self._df['last'] ) /3).rolling(window=self._lookback).sum()
        self._df['cum_vol_price'] = (self._df['volume'] * self._df['last']).rolling(window=self._lookback).sum()
        self._df['vwap'] = self._df['cum_vol_price'] / self._df['cum_vol']

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        self._df['stance'] = np.where(self._df['last'] >=  self._df['vwap'], 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['last'] <  self._df['vwap'], -1, self._df['stance'])
        

