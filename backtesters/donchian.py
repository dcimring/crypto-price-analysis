'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
from backtester import Backtester

class DonchianBacktester(Backtester):
    '''Backtest for the "Donachian" strategy

    Long on new 55 day high, close on 20 day low
    Short on new 55 day low, close on 20 day high

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    entry: (int) how many days for long / short entry calculation
    exit : (int) how many days for long / short exit calculation
    '''

    def __init__(self, series, entry=55, exit=20):
        self._entry = entry
        self._exit = exit
        super(DonchianBacktester,self).__init__(series,long_only=False)

    def __str__(self):
        return "Donchian Backtest Strategy (entry=%d, exit=%d, long_only=%s, start=%s, end=%s)" % (
            self._entry, self._exit, False, str(self._start_date), str(self._end_date))


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        
        current_stance = 0
        stances = []

        long_entry_level = self._df['last'].rolling(window=self._entry).max()
        long_exit_level = self._df['last'].rolling(window=self._exit).min()
        short_entry_level = self._df['last'].rolling(window=self._entry).min()
        short_exit_level = self._df['last'].rolling(window=self._exit).max()


        for index in np.arange(0,len(self._df)):

            long_signal = False
            short_signal = False
            long_close = False
            short_close = False
            close = self._df['last'].iloc[index]
            
            if close >= long_entry_level[index]:
                long_signal = True

            if close <= short_entry_level[index]:
                short_signal = True

            if close <= long_exit_level[index]:
                long_close = True

            if close >= short_exit_level[index]:
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
        
        

