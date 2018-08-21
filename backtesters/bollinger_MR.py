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

class BollingerMR(Backtester):
    '''

    %B = Close - B lower / (B upper - B lower)
    Smoothe with a 3 day MA
    If close above 200d MA and B < 0.25 buy
    Close long if BB% > 0.75
    If close below 200d MA and B > 0.75 short
    Cover short if BB% < 0.25

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    trend: (int) lookback period for moving average to determine trend
    lookback (int) lookckback period for billinger
    threshhold : (float) cut off point when looking at %B
    '''

    def __init__(self, series, trend=200, lookback=14, threshhold=0.25):
        self._trend = trend
        self._threshhold = threshhold
        self._lookback = lookback
        super(BollingerMR,self).__init__(series,long_only=False)

    def __str__(self):
        return "Bollinger MR Backtest (trend=%d, threshhold=%0.2f, lookback=%d, long_only=%s, start=%s, end=%s)" % (
            self._trend, self._threshhold, self._lookback, False, str(self._start_date), str(self._end_date))

    def plot(self, start_date=None, end_date=None, figsize=None):
        '''Plot of prices and the the buy and sell points
        Stratgies can add their own additional indicators
        '''

        sns.set_style("white")
        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, figsize=figsize, gridspec_kw = {'height_ratios':[3, 1]})
        fig.suptitle(self.__str__(), size=13)
        Backtester.plot(self,start_date=start_date,end_date=end_date, ax=ax1)
        temp = self._df.loc[start_date:end_date]
        # ax1.legend()

        ax1.plot(temp['trend'], label='trend`')
        
        ax1.plot(temp['lower'], color='silver', alpha=0.5, label = 'bollinger')
        #ax.plot(temp['middle'], color='silver')
        ax1.plot(temp['upper'], color='silver', alpha=0.5, label = 'bollinger')

        ax1.fill_between(temp.index,temp['lower'],temp['upper'], alpha=0.2, color='silver')

        ax1.legend()

        ax2.plot(temp['B%'] * 100)
        ax2.hlines(self._threshhold * 100,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        ax2.hlines((1-self._threshhold) * 100,temp.index[0],temp.index[-1],colors="silver",linestyles="dashed")
        ax2.set_ylim(0,100)
        ax2.set_ylabel('B%')

        plt.tight_layout()
        plt.show()


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        self._df['trend'] = self._df['last'].rolling(window=self._trend).mean()
        self._df['upper'], self._df['middle'], self._df['lower'] = talib.BBANDS(self._df['last'], timeperiod=self._lookback)
        B = (self._df['last'] - self._df['lower']) / (self._df['upper'] - self._df['lower']) # %B
        self._df['B%'] = B.rolling(window=3).mean() # smoothed version of %B
        
        current_stance = 0
        stances = []


        for index in np.arange(0,len(self._df)):

            long_signal = False
            short_signal = False
            long_close = False
            short_close = False
            close = self._df['last'].iloc[index]
            
            if close >= self._df['trend'].iloc[index]:
                if self._df['B%'].iloc[index] < self._threshhold: 
                    long_signal = True

            if close < self._df['trend'].iloc[index]:
                if self._df['B%'].iloc[index] > (1-self._threshhold):
                    short_signal = True

            if self._df['B%'].iloc[index] > (1-self._threshhold):
                long_close = True

            if self._df['B%'].iloc[index] < self._threshhold:
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
        
        

