'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class HABacktester(Backtester):
    '''Backtest a Heikin Ashi strategy
    See https://www.investopedia.com/trading/heikin-ashi-better-candlestick/

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    opens: (Panda Series) a list of CLOSE prices by date
    highs: (Panda Series) a list of CLOSE prices by date
    lows: (Panda Series) a list of CLOSE prices by date
    long_only (Boolean) True if you can go long only (no shorts)
    '''

    def __init__(self, series, opens, highs, lows, long_only=False):
        super(HABacktester,self).__init__(series,long_only=long_only)
        self._df['open'] = opens
        self._df['high'] = highs
        self._df['low'] = lows

    def __str__(self):
        return "Heikin Ashi Backtest Strategy (long_only=%s, start=%s, end=%s)" % (
            str(self._long_only),str(self._start_date), str(self._end_date))


    def _indicators(self):

        #self._df['ha_last'] = (self._df['open'] + self._df['high'] + self._df['low'] + self._df['last']) / 4
        #self._df['ha_open'] = 

        ha_Open_list = []
        ha_High_list = []
        ha_Low_list = []
        ha_Close_list = []
        i = 0
        while i < len(self._df['last']):
            if i is 0:
                ha_Open = (self._df['open'][i] + self._df['last'][i]) / 2
                ha_Close = (self._df['open'][i] + self._df['high'][i] + self._df['low'][i] + self._df['last'][i]) / 4
                ha_High = self._df['high'][i]
                ha_Low = self._df['low'][i]
            else:
                ha_Open = (ha_Open_list[i - 1] + ha_Close_list[i - 1]) / 2
                ha_Close = (self._df['open'][i] + self._df['high'][i] + self._df['low'][i] + self._df['last'][i]) / 4
                ha_High = max([self._df['high'][i], ha_Open, ha_Close])
                ha_Low = min([self._df['low'][i], ha_Open, ha_Close])
            ha_Open_list.append(ha_Open)
            ha_High_list.append(ha_High)
            ha_Low_list.append(ha_Low)
            ha_Close_list.append(ha_Close)
            i += 1
        
        self._df['ha_open'] = ha_Open_list
        self._df['ha_last'] = ha_Close_list
        self._df['ha_low'] = ha_Low_list
        self._df['ha_high'] = ha_High_list

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        self._df['stance'] = np.where(self._df['ha_last'] >= self._df['ha_open'], 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['ha_last'] < self._df['ha_open'], -1, self._df['stance'])
        

