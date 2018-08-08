'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
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
    max_positions: (int) maximum number of positions open at any time
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=7,threshhold=0.2,hold=7,max_positions=1,long_only=True):
        self._threshhold = threshhold
        self._lookback = lookback
        self._hold = hold
        self._max_positions = max_positions
        super(YaleBacktester,self).__init__(series,long_only=long_only)

    def __str__(self):
        return "Yale Backtest Strategy (lookback=%d, threshhold=%0.3f, hold=%d, max_positions=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, self._threshhold, self._hold, self._max_positions, str(self._long_only), str(self._start_date), str(self._end_date))

    def trades(self):
        '''Return a Pandas DataFrame with details of each trade
        Needs to override its base class since each trade last 7 days
        and buy / sells from different trades will get mixed up
        '''
        self._make_sure_has_run()
        buy = self._df['buy'].dropna()
        sell = self._df['sell'].dropna()
        r = []
        
        for date, price in buy.iteritems(): 
            try:
                sell_date = date + timedelta(days=7)
                sell_price = self._df.loc[sell_date,'last']
            except IndexError: # its the end of the time series
                sell_price = self._df['last'].iloc[-1] # current price
                sell_date = self._df['last'].index[-1] # current date
            finally:
                days = (sell_date - date).days 
                r.append((date,"Long",round(price,6),round(sell_price,6),days,sell_price/price-1))   


        df = pd.DataFrame(sorted(r, key = lambda x: x[0]))
        df.columns = ['Date','Type','Entry','Exit','Days','Return%']
        df['Return%'] = np.round(df['Return%'] * 100,2)
        df.set_index('Date', inplace=True)

        return df

    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        
        current_stance = 0
        stances = []
        count_down = 0
        stances.append(0) # first day you can't make a trade

        for index in np.arange(1,len(self._df)):
            
            if self._df['last'].iloc[index]/self._df['last'].iloc[index-self._lookback] >= (1+self._threshhold):
                if current_stance < self._max_positions:
                    current_stance += 1
                    count_down += (self._hold + 1)

            if current_stance > 0 and count_down % (self._hold + 1) == 1:
                current_stance -= 1
            
            if count_down > 0: count_down -= 1

            stances.append(current_stance)

        self._df['stance'] = stances
        self._df['stance'] /= self._max_positions
        

