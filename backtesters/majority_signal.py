'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from portfolio import PortfolioBacktester
from IPython.core.debugger import set_trace


class MajoritySignalBacktester(PortfolioBacktester):
    '''Backtest a combination of strategies
    Add up all the long / short signals from each strategy
    If total > 0 then long, else short

    # todo - rather initialise with 1 data series and multiple strategies to combine
    # on that series

    Parameters:
    strategies: (list) a list of strategies
    weights: (list) optional list of weights, if None then equal weights assumed
    '''

    def __init__(self, strategies=None, weights=None):
        
        super(MajoritySignalBacktester,self).__init__(strategies=strategies, weights=weights)

    def plot(self, start_date=None, end_date=None, figsize=None, ax=None):
        self._make_sure_has_run()
        temp = self._df.loc[start_date:end_date]
       
        if ax is None:
            fig, ax = plt.subplots(figsize=figsize)

        ax.plot(temp['last'], label='Price')
        ax.plot(temp['buy'],color='g', linestyle='None', marker='^')
        ax.plot(temp['sell'],color='r', linestyle='None', marker='v')

        return ax

    def _trade_logic(self):
        '''Add up all the short long signals
        '''

        for i, s in enumerate(self._strategies):
            s._run()
            if i==0:
                self._df = self._strategies[0]._df.copy()
                self._df['stance'] =  s._df['stance'] * self._weights[i]
            else:
                self._df['stance'] +=  s._df['stance'] * self._weights[i]
                #self._df['trade'] +=  s._df.reindex(self._df.index, fill_value=0)['trade']
                #self._df['market'] += s._df.reindex(self._df.index, fill_value=0)['market'] * self._weights[i]
                #self._df['strategy'] += s._df.reindex(self._df.index, fill_value=0)['strategy'] * self._weights[i]

        # If majority signal is long then go long, if majority signal is short go short
        self._df['stance'] = np.where(self._df['stance'] < 0,-1,self._df['stance'])
        self._df['stance'] = np.where(self._df['stance'] > 0,1,self._df['stance'])

        self._df['trade'] = np.where(self._df['stance'] != self._df['stance'].shift(1).fillna(0), 1, 0)
        self._df['strategy'] = self._df['market'] * self._df['stance'].shift(1) #shift(1) means day before

        # needed for chart
        #self._df['last'] = self._df['market'].cumsum().apply(np.exp).dropna()
        self._df['buy'] = np.where( self._df['stance'] - self._df['stance'].shift(1).fillna(0) > 0, self._df['last'], np.NAN)
        self._df['sell'] = np.where( self._df['stance'] - self._df['stance'].shift(1).fillna(0) < 0, self._df['last'], np.NAN)


    