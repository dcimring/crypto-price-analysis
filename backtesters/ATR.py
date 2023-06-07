'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import talib
from backtester import Backtester
from IPython.core.debugger import set_trace

class ATRMomentum(Backtester):
    '''

    Momentum strategy based on ATR (average true range)
    If you touch then upper band you go long until you cross the middle band
    If you touch then lower band you go short until you cross the middle band
    Middle band is a simple moving average

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback (int) lookckback period for billinger
    distance : (float) number of std deviations for the band
    '''

    def __init__(self, series, high=None, low=None, lookback=14, distance=2):
        self._lookback = lookback
        self._distance = distance
        super(ATRMomentum,self).__init__(series,long_only=False)

        if high is None:
            self._df['high'] = self._df['last']
        else:
            self._df['high'] = high

        if low is None:
            self._df['low'] = self._df['last']
        else:
            self._df['low'] = low

    def __str__(self):
        return "ATR Momentum Backtest (lookback=%d, distance=%0.1f, start=%s, end=%s)" % (
            self._lookback, self._distance, str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        '''Plot of prices and the the buy and sell points
        Stratgies can add their own additional indicators
        '''

        sns.set_style("white")
        fig, ax = plt.subplots(figsize=figsize)
        fig.suptitle(self.__str__(), size=13)
        Backtester.plot(self,start_date=start_date,end_date=end_date, ax=ax)
        temp = self._df.loc[start_date:end_date]
        # ax1.legend()
   
        ax.plot(temp['lower'], color='silver', alpha=0.5, label = 'bollinger')
        ax.plot(temp['middle'],"--", color='silver', alpha=0.3)
        ax.plot(temp['upper'], color='silver', alpha=0.5, label = 'bollinger')

        ax.fill_between(temp.index,temp['lower'],temp['upper'], alpha=0.2, color='silver')

        ax.legend()
        plt.tight_layout()
        plt.Xlable("axe des x")

        plt.show()


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        ATR = talib.ATR(self._df['high'], self._df['low'], self._df['last'], timeperiod=self._lookback)
        #set_trace()

        self._df['middle'] = self._df['last'].rolling(window=self._lookback).mean()
        self._df['upper'] = self._df['middle'] + (self._distance * ATR)
        self._df['lower'] = self._df['middle'] - (self._distance * ATR)
        
        current_stance = 0
        stances = []


        for index in np.arange(0,len(self._df)):

            long_signal = False
            short_signal = False
            long_close = False
            short_close = False
            close = self._df['last'].iloc[index]
            
            if close >= self._df['upper'].iloc[index]:
                long_signal = True

            if close < self._df['lower'].iloc[index]:
                short_signal = True

            if close <= self._df['middle'].iloc[index]:
                long_close = True

            if close >= self._df['middle'].iloc[index]:
                short_close = True

            if current_stance == 0:
                if long_signal:
                    current_stance = 1
                elif short_signal:
                    current_stance = -1
            elif current_stance == 1:
                if long_close:
                    current_stance = 0
            elif current_stance == -1:
                if short_close:
                    current_stance = 0

            stances.append(current_stance)

        self._df['stance'] = stances
        
        

