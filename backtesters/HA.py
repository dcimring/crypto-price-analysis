'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.finance import candlestick2_ohlc
import math
from backtester import Backtester
import indicators.heikenashi
reload(indicators.heikenashi)
from indicators.heikenashi import HeikenAshi

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

    def __init__(self, series, opens, highs, lows, long_only=False, slippage=0):
        super(HABacktester,self).__init__(series,long_only=long_only, slippage=slippage)
        self._df['open'] = opens
        self._df['high'] = highs
        self._df['low'] = lows

    def __str__(self):
        return "Heikin Ashi Backtest Strategy (long_only=%s, start=%s, end=%s)" % (
            str(self._long_only),str(self._start_date), str(self._end_date))

    def candlestick(self, start_date=None, end_date=None, figsize=None):

        self._make_sure_has_run()
        temp = self._df.loc[start_date:end_date]
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_title(self.__str__(), size=13)

        xdates = [i.strftime("%Y-%m-%d") for i in temp.index]
        steps = int(math.ceil(len(temp)/62.0))
        ax.set_xticks(np.arange(len(temp), step = steps))
        ax.set_xticklabels(xdates[::steps], rotation=90)
        
        candlestick2_ohlc(ax,temp['ha_open'],temp['ha_high'],temp['ha_low'],temp['ha_last'],width=0.6, colorup='#77d879', colordown='#db3f3f')

    def _indicators(self):
        
        ha = HeikenAshi(self._df[['last','open','high','low']])

        self._df['ha_open'] = ha['ha_open']
        self._df['ha_last'] = ha['ha_last']
        self._df['ha_low'] = ha['ha_low']
        self._df['ha_high'] = ha['ha_high']

        # Try adding MA crossover as well
        self._df['ms'] = np.round(self._df['last'].rolling(window=10).mean(), 8)
        self._df['ml'] = np.round(self._df['last'].rolling(window=21).mean(), 8)
        self._df['mdiff'] = self._df['ms'] - self._df['ml']

        # What about comparing todays average price to yesterdays
        self._df['avg_price'] = (self._df['open'] + self._df['last']) / 2

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        # self._df['stance'] = np.where( (self._df['avg_price'] >= self._df['avg_price'].shift(1)) , 1, -1)

        self._df['stance'] = np.where( (self._df['ha_last'] >= self._df['ha_open']) , 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where( (self._df['ha_last'] < self._df['ha_open']) , -1, self._df['stance'])
        

