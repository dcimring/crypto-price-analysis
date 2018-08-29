'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from backtester import Backtester
from IPython.core.debugger import set_trace


class PortfolioBacktester(Backtester):
    '''Backtest a combination of strategies

    Parameters:
    strategies: (list) a list of strategies
    weights: (list) optional list of weights, if None then equal weights assumed
    '''

    def __init__(self, strategies=None, weights=None):
        
        if not strategies:
            raise ValueError('Strategy list is empty')
        
        if weights is None:
            self._weights = np.ones(len(strategies)) / len(strategies)
        else:
            if len(weights) != len(strategies): raise ValueError('Stategy and Weighs mismatch')
            if not np.isclose(sum(weights),1): weights = np.array(weights) / float(sum(weights))
            self._weights = weights

        self._strategies = strategies
        self._has_run = False
        self._long_only = False;

        # If strategies contain dates with different time zones then this becomes an issue
        # Setting time zone to none below solves some issues but creates new issues for reindex in _trade_logic()
        # Need to look into adjusting all strategy dates for time zones before combining them

        start_dates, end_dates = [],[]
        for s in self._strategies:
            start_dates.append(s._df.index[0]) # .replace(tzinfo=None)
            end_dates.append(s._df.index[-1]) # .replace(tzinfo=None)

        self._start_date = min(start_dates)
        self._end_date = max(end_dates)

        index = pd.DatetimeIndex(start = self._start_date, end = self._end_date, freq='d')
        self._df = pd.DataFrame(index=index, columns=['strategy','market','stance','trade']).fillna(0)


    def __str__(self):
        r = ''
        for s in self._strategies:
            r += s.__str__() + "\n"
        return r

    def plot(self, start_date=None, end_date=None, figsize=None):
        '''Plot a chart for each strategy'''
        for i, s in enumerate(self._strategies):
            s.plot(start_date=start_date, end_date=end_date, figsize=figsize)

    def _trade_logic(self):
        '''Combine the stance from all strategies
        '''

        for i, s in enumerate(self._strategies):
            s._run()
            self._df['stance'] +=  s._df.reindex(self._df.index, fill_value=0)['stance']
            self._df['trade'] +=  s._df.reindex(self._df.index, fill_value=0)['trade']
            self._df['market'] += s._df.reindex(self._df.index, fill_value=0)['market'] * self._weights[i]
            self._df['strategy'] += s._df.reindex(self._df.index, fill_value=0)['strategy'] * self._weights[i]


    def _run(self):

        if self._has_run:
            return

        self._trade_logic()

        #set_trace()

        self._df['strategy_last'] = self._df['strategy'].cumsum().apply(np.exp).dropna() # needed for drawdown calculations

        # since we are using log returns multiplying by -1 for shorts works

        start_date, end_date = self._df.index[0], self._df.index[-1]
        years = (end_date - start_date).days / 365.25

        #self._df['trade'] = np.where(self._df['stance'] != self._df['stance'].shift(1).fillna(0), 1, 0)
        trades = self._df['trade'].sum()
        market = ((np.exp(self._df['market'].cumsum()[-1]) - 1) * 100)
        market_pa = ((market / 100 + 1) ** (1 / years) - 1) * 100
        strategy = ((np.exp(self._df['strategy'].cumsum()[-1]) - 1) * 100)
        strategy_pa = ((strategy / 100 + 1) ** (1 / years) - 1) * 100
        #set_trace()
        # Calculating sharpe using log returns
        # For daily data you annualise with sqrt(365.25)
        sharpe = math.sqrt(365.25) * np.average(self._df['strategy'].dropna()) / np.std(self._df['strategy'].dropna())
        market_sharpe = math.sqrt(365.25) * np.average(self._df['market'].dropna()) / np.std(self._df['market'].dropna())
        self._results = {"Strategy":np.round(strategy,2), "Market":np.round(market,2),"Trades":trades,"Sharpe":np.round(sharpe,2),
                        "Strategy_pa": np.round(strategy_pa,2), "Market_pa": np.round(market_pa,2), "Years": np.round(years,2),
                        "Trades_per_month":np.round(trades/years/12,2),"Market_sharpe":np.round(market_sharpe,2),
                        'Current_stance':self._df['stance'].iloc[-1]}
        self._has_run = True

        

        

