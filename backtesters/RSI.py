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

    def __init__(self, series, lookback=14, long_only=False):
        self._lookback=lookback
        Backtester.__init__(self,series,long_only=long_only)

    def __str__(self):
        return "RSI Backtest Strategy (lookback=%d, long_only=%s, start=%s, end=%s)" % (
            self._lookback, str(self._long_only), str(self._start_date), str(self._end_date))


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''
        self._df['stance'] = 1

