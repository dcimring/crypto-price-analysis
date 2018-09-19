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

        # See https://github.com/joosthoeks/jhTAlib/blob/master/jhtalib/data/data.py
        # And https://stackoverflow.com/questions/40613480/heiken-ashi-using-pandas-python
        # And https://quantiacs.com/Blog/Intro-to-Algorithmic-Trading-with-Heikin-Ashi.aspx
        # And https://github.com/Quantiacs/HeikinAshi/blob/master/heikinAshi.py

        # HA open = yesterday's (O+C)/2
        # But do you use O and C price from yesterday or do you use O and C HA values from yesterday?
        # Comparing to TradingView it seems using yesterdays HA values is a better match for their chart

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
                #ha_Open = (self._df['open'][i] + self._df['open'][i-1]) / 2
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

        # Try adding MA crossover as well
        self._df['ms'] = np.round(self._df['last'].rolling(window=10).mean(), 8)
        self._df['ml'] = np.round(self._df['last'].rolling(window=21).mean(), 8)
        self._df['mdiff'] = self._df['ms'] - self._df['ml']

        # What about comparing todays average price to yesterdays
        self._df['avg_price'] = (self._df['open'] + self._df['high'] + self._df['low'] + self._df['last']) / 4

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._indicators()
        
        # self._df['stance'] = np.where( (self._df['avg_price'] >= self._df['avg_price'].shift(1)) , 1, -1)

        self._df['stance'] = np.where( (self._df['ha_last'] >= self._df['ha_open']) , 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where( (self._df['ha_last'] < self._df['ha_open']) , -1, self._df['stance'])
        

