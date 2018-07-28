'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import talib
from backtester import Backtester

class WilliamsRBacktester(Backtester):
    '''Backtest a RSI strategy

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=14, buy_on=-20, sell_on=-20, long_only=False):
        self._lookback=lookback
        self._buy_on=buy_on
        self._sell_on=sell_on
        super(WilliamsRBacktester,self).__init__(series,long_only=long_only)

    def __str__(self):
        return "Williams%%R Backtest Strategy (lookback=%d, buy_on=%d, sell_on=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, self._buy_on, self._sell_on, str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("dark")
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=figsize, gridspec_kw = {'height_ratios':[3, 1]})
        fig.suptitle(self.__str__(), size=13)

        Backtester.plot(self,start_date=start_date,end_date=end_date, ax=ax1)
        temp = self._df.loc[start_date:end_date]
        ax1.legend()
        
        ax2.plot(temp['%R'])
        ax2.hlines(self._buy_on,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        ax2.hlines(self._sell_on,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        ax2.set_ylim(-105,5)
        ax2.set_ylabel('%R')
        #ax2.invert_yaxis()
        
        plt.tight_layout()
        plt.show()

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        
        self._df['%R'] = talib.WILLR(self._df['last'], self._df['last'], self._df['last'], timeperiod=self._lookback)

        # long when RSI is high, short when it is low, in cash otherwise
        # there are other strategies
        # https://tradingsim.com/blog/rsi-relative-strength-index/

        self._df['stance'] = np.where(self._df['%R'] >= self._buy_on, 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['%R'] <= self._sell_on, -1, self._df['stance'])


