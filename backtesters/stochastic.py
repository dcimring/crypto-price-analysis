'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import talib
from backtester import Backtester

class StochasticBacktester(Backtester):
    '''Backtest a strategy where you are long if the price today is a new 
    high over the lookback period, or within tolerance of a high

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, high, low, K=5, D=3, smoothe=3, buy_on=20, sell_on=80, long_only=False):
        self._K = K
        self._D = D
        self._buy_on = buy_on
        self._sell_on = sell_on
        self._smoothe = smoothe
        super(StochasticBacktester,self).__init__(series,long_only=long_only)
        self._df['high'] = high
        self._df['low'] = low
            

    def __str__(self):
        return "Stochastic Backtest Strategy (K=%d, D=%d, smoothe=%d, buy_on=%d, sell_on=%d, long_only=%s, start=%s, end=%s)" % (
            self._K, self._D, self._smoothe, self._buy_on, self._sell_on, str(self._long_only), str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        sns.set_style("dark")
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=figsize, gridspec_kw = {'height_ratios':[3, 1]})
        fig.suptitle(self.__str__(), size=13)

        Backtester.plot(self,start_date=start_date,end_date=end_date, ax=ax1)
        temp = self._df.loc[start_date:end_date]
        ax1.legend()
        
        ax2.plot(temp['slowk'] , label='K')
        ax2.plot(temp['slowd'] , label='D')
        ax2.hlines(self._buy_on,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        ax2.hlines(self._sell_on,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        ax2.set_ylim(0,100)
        ax2.set_ylabel('Stochastic')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._df['slowk'], self._df['slowd'] = talib.STOCH(self._df['high'], self._df['low'], self._df['last'], fastk_period=self._K, slowk_period=self._smoothe, slowk_matype=0, slowd_period=self._D, slowd_matype=0)
        
        # buy when below 20 and K crosses over D
        # sell when above 80 and K crossed below D
        
        current_stance = 0
        stances = []

        for index, row in self._df.iterrows():
            buy_signal = False
            sell_signal = False
            if (row['slowd'] < self._buy_on) and (row['slowk'] > row['slowd']):
                buy_signal = True
            if (row['slowd'] > self._sell_on) and (row['slowk'] < row['slowd']):
                sell_signal = True

            if current_stance == 0:
                if buy_signal:
                    current_stance = 1
                    if sell_signal and not self._long_only:
                        current_stance = -1
            elif current_stance == 1:
                if sell_signal:
                    current_stance = 0
                    if not self._long_only:
                        current_stance = -1
            else:
                if buy_signal: current_stance = 1
            stances.append(current_stance)

        self._df['stance'] = stances



