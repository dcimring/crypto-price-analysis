'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class YaleBacktester(Backtester):
    '''Backtest a the straegy from this article:

    https://www.cnbc.com/2018/08/08/yale-economists-share-strategy-for-buying-bitcoin-ripple-ethereum.html
    http://www.nber.org/papers/w24877.pdf
    
    Buy bitcoin after its price already had a sharp increase (20 percent in a single week)
    Sell seven days after buying.

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) how many days back to calculate price change
    threshhold: (float) price needs to increase by this to buy
    hold: (int) how many days to hold
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=7,threshhold=0.2,hold=7,long_only=True):
        self._threshhold = threshhold
        self._lookback = lookback
        self._hold = hold
        super(YaleBacktester,self).__init__(series,long_only=long_only)

    def __str__(self):
        return "Yale Backtest Strategy (lookback=%d, threshhold=%0.3f, hold=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, self._threshhold, self._hold, str(self._long_only), str(self._start_date), str(self._end_date))


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        
        # todo - cater for more than 1 position at a time

        current_stance = 0
        stances = []
        count_down = self._hold
        stances.append(0) # first day you can't make a trade

        for index in np.arange(1,len(self._df)):
            
            buy_signal = False
            sell_signal = False
            
            if self._df['last'].iloc[index]/self._df['last'].iloc[index-self._lookback] >= (1+self._threshhold):
                buy_signal = True

            if count_down == 0:
                sell_signal = True
            
            if current_stance == 0:
                if buy_signal:
                    current_stance = 1
                    count_down = self._hold
            
            elif current_stance == 1:
                if sell_signal:
                    current_stance = 0
            
            count_down -= 1
            
            stances.append(current_stance)

        self._df['stance'] = stances
        

