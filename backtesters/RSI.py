'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class RSIBacktester(Backtester):
    '''Backtest a RSI strategy

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    lookback: (int) lookback period
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, lookback=14, buy_on=30, sell_on=70, long_only=False):
        self._lookback=lookback
        self._buy_on=buy_on
        self._sell_on=sell_on
        super().__init__(self,series,long_only=long_only)

    def __str__(self):
        return "RSI Backtest Strategy (lookback=%d, buy_on=%d, sell_on=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, self._buy_on, self._sell_on, str(self._long_only), str(self._start_date), str(self._end_date))


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        delta = self._df['last'].diff()
        dUp, dDown = delta.copy(), delta.copy()
        dUp[dUp < 0] = 0
        dDown[dDown > 0] = 0

        RolUp = dUp.rolling(window=self._lookback).mean()
        RolDown = dDown.abs().rolling(window=self._lookback).mean()

        RS = RolUp / RolDown
        RSI = 100.0 - (100.0 / (1.0 + RS))
        self._df['RSI'] = RSI



        self._df['stance'] = 1

