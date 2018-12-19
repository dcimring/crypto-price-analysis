'''Backtest a strategy that keeps choosing the best MA pair from the past x days
and uses that until a better MA pair is found
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ipywidgets import IntProgress
from IPython.display import display
from backtester import Backtester
from MA import MABacktester

from IPython.core.debugger import set_trace

class MALiveOptimiseBacktester(Backtester):
    '''Backtest a strategy that keeps choosing the best MA pair from the past x days
    and uses that until a better MA pair is found


    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period for optimisation
    strats: (list) list of MA params
    '''

    def __init__(self, series, lookback = 90, strats = [(1,7),(1,4)]):
        
        super(MALiveOptimiseBacktester,self).__init__(series,long_only=False)

        self._lookback = lookback
        self._strats = strats


    def __str__(self):
        return "MA Live Optimise Backtest (lookback=%d, strats=%s, start=%s, end=%s)" % (
            self._lookback, str(self._strats), str(self._start_date), str(self._end_date))


    def _indicators(self):
        
        a,b = zip(*self._strats)
        ma_list = set(a+b)
        for ma in ma_list:
            self._df[str(ma)] = self._df['last'].rolling(window=ma).mean()

    def _find_best_strat(self, data):
        
        # is there only 1 strategy?
        if len(self._strats) == 1:
            return self._strats[0]

        best_ret = -100
        best_strat = None
        
        for strat in self._strats:
            ret = MABacktester(data,strat[0],strat[1]).results()['Strategy']
            if ret > best_ret:
                best_ret = ret
                best_strat = strat
        return best_strat


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        max_count = len(self._df)
        bar = IntProgress(min=0, max=max_count) # instantiate a progress bar
        display(bar) # display the bar

        self._indicators()

        current_stance = 0
        stances = []
        
        i = 0

        for date, row in self._df.iterrows():
            
            if i>=self._lookback:
                strat = self._find_best_strat(self._df['last'].iloc[i-self._lookback:i])
            else:
                strat = self._strats[0]

           
            buy_signal = False
            sell_signal = False
            
            ms = str(strat[0])
            ml = str(strat[1])

            if row[ms] >= row[ml]:
                buy_signal = True
            else:
                sell_signal = True

            # If the ma values are not avail yet then stay neutral
            if np.isnan(row[ml]):
                buy_signal = False
                sell_signal = False

            if current_stance == 0:
                if buy_signal:
                    current_stance = 1
                    
                if sell_signal:
                    current_stance = -1
                    

            elif current_stance == 1:
                if sell_signal:
                    current_stance = -1
                    
                    
            else: # you are -1
                if buy_signal:
                    current_stance = 1
                    

            stances.append(current_stance)
            i+=1
            bar.value += 1

        self._df['stance'] = stances
        
