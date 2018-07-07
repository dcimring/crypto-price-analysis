'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester

class PortfolioBacktester(Backtester):
    '''Backtest a combination of strategies

    Parameters:
    strategies: (list) a list of strategies
    '''

    def __init__(self, strategies=None):
        if not strategies:
            raise ValueError('Strategy list is empty')
        self._strategies = strategies
        self._has_run = False
        self._long_only = False;

    def __str__(self):
        r = ''
        for s in self._strategies:
            r += s.__str__() + "\n"
        return r

    def _trade_logic(self):
        '''Combine the stance from all strategies
        '''

        for i, s in enumerate(self._strategies):
            s._run()
            if i==0:
                self._df = s._df['last'].copy().to_frame()
                self._df.columns = ['last']
                self._df['stance'] = s._df['stance']
                #self._df.head(10)
                continue
            self._df['stance'] += s._df['stance']

        self._df['stance'] = self._df['stance'] / len(self._strategies)
        

