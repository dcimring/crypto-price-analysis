'''Backtest Moving Average (MA) crossover strategies
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class MABacktester(object):
    '''Backtest a Moving Average (MA) crossover strategy

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    ms: (int) short moving average
    ml: (int) long moving average
    long_only: (boolean) True if the strategy can only go long
    ema: (boolean) True if you want exponential MA's
    '''

    def __init__(self, series, ms=1, ml=10, long_only=False, ema=False):
        self._df = series.to_frame().dropna()
        self._df.columns = ['last']
        self._ms = ms
        self._ml = ml
        self._ema = ema
        self._long_only = long_only
        self._results = {}
        self._has_run = False

    def __str__(self):
        start_date = self._df.index[0].strftime('%Y-%m-%d')
        end_date = self._df.index[-1].strftime('%Y-%m-%d')
        return "MA Backtest Strategy (ms=%d, ml=%d, ema=%s, long_only=%s, start=%s, end=%s)" % (
            self._ms, self._ml, str(self._ema), str(self._long_only), str(start_date), str(end_date))

    def _make_sure_has_run(self):
        if not self._has_run:
            self._run()

    def results(self):
        self._make_sure_has_run()
        return self._results

    def last(self):
        return self._df['last']

    def strategy_last(self):
        self._make_sure_has_run()
        return self._df['strategy_last']

    def strategy_ret(self):
        self._make_sure_has_run()
        return self._df['strategy']

    def market_ret(self):
        self._make_sure_has_run()
        return self._df['market']     

    def stance(self):
        self._make_sure_has_run()
        return self._df['stance']     


    def ml(self):
        self._make_sure_has_run()
        return self._df['ml']

    def ms(self):
        self._make_sure_has_run()
        return self._df['ms']

    def buy(self):
        self._make_sure_has_run()
        return self._df['buy']

    def sell(self):
        self._make_sure_has_run()
        return self._df['sell']

    def _sum_returns(self, returns, groupby):
        '''
        Returns must be log returns
        '''
        return np.exp(returns.groupby(groupby).sum()) - 1

    def trades(self):
        '''Return a list of tuples containing trade data
        Each tuple is (buy_price, sell_price, days_held)
        '''
        self._make_sure_has_run()
        buy = self._df['buy'].dropna()
        sell = self._df['sell'].dropna()
        r = []
        for date, price in buy.iteritems():
            sell_price = sell.loc[date:][0] # find next sell
            sell_date = sell.loc[date:].index[0] # and the date sold
            days = (sell_date - date).days
            r.append((round(price,2),round(sell_price,2),days))   
        return r

    def plot(self, start_date=None, end_date=None, figsize=None):
        '''Plot of prices, MA's, and indicators for the buy and sell points
        '''
        self._make_sure_has_run()
        temp = self._df.loc[start_date:end_date]
        plt.figure(figsize=figsize)
        plt.plot(temp['last'])
        plt.plot(temp['ml'])
        if self._ms > 1:
            plt.plot(temp['ms'])
        plt.plot(temp['buy'],color='g', linestyle='None', marker='^')
        plt.plot(temp['sell'],color='r', linestyle='None', marker='v')
        plt.show()

    def plot_equity_curve(self, start_date=None, end_date=None, figsize=None):
        '''Plot an equity curve for the strategy versus
        the market'''
        self._make_sure_has_run()
        self._df[['market','strategy']].loc[start_date:end_date].cumsum().apply(np.exp).plot(figsize=figsize)

    def plot_heatmap(self, target="strategy", figsize=None):
        '''Draw a heatmap of returns

        Parameters:
        target: (string) "strategy" or "market"
        '''
        self._make_sure_has_run()
        if target == "strategy":
            returns = self._df['strategy'].copy()
        else:
            returns = self._df['market'].copy()
        original_returns = returns.copy()
        returns_index = returns.resample('MS').first().index
        returns_values = self._sum_returns(returns, (returns.index.year, returns.index.month)).values
        returns = pd.DataFrame(index=returns_index, data={'Returns': returns_values})

        returns['Year'] = returns.index.strftime('%Y')
        returns['Month'] = returns.index.strftime('%b')

        # make pivot table
        returns = returns.pivot('Year', 'Month', 'Returns').fillna(0)

         # handle missing months
        for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                      'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
            if month not in returns.columns:
                returns.loc[:, month] = 0

        # order columns by month
        returns = returns[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                           'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]

        returns['Total'] = self._sum_returns(original_returns, original_returns.index.year).values

        returns *= 100

        fig, ax = plt.subplots(figsize=figsize)
        ax = sns.heatmap(returns, ax=ax, annot=True, center=0, annot_kws={"size": 11}, fmt="0.1f",
                         linewidths=0.5, square=True, cbar=False, cmap='RdYlGn', vmin=-100, vmax=100)
        ax.set_title("Monthly Returns (%)\n", fontsize=14, color="black", fontweight="bold")
        ax.tick_params(axis=u'both', which=u'both',length=0)
        ax.xaxis.label.set_visible(False)
        ax.yaxis.label.set_visible(False)

        fig.subplots_adjust(hspace=0)
        plt.yticks(rotation=0)
        plt.show()

    def _max_dd(self, xs, ds, depth = 5):
        '''
        Create a list of largest drawdowns recursively
         
        Parameters:
        xs: (numpy array) of prices
        ds: (numpy array) of dates
         
        Return:
        A list of tuples with drawdown size, high and low value, high and low date
        '''

        if depth <= 0:
            return []
        try:
            i = np.argmax( (np.maximum.accumulate(xs) - xs) / xs ) #low
            j = np.argmax(xs[:i]) #high
            dd = np.round( (1- xs[i]/xs[j]) * 100, 2) #drawdown size
            return [(dd,xs[j],xs[i],ds[j],ds[i])] + self._max_dd(xs[:j],ds[:j],depth-1) + self._max_dd(xs[i:],ds[i:],depth-1)
        except:
            return []


    def drawdowns(self, target="strategy", cutoff = 25):
        '''Create a list of drawdowns

        Parameters:
        target: (string) set to "strategy" or "market"
        cutoff: (int) only show drawdowns larger than this, eg 25 is 25%

        Return:
        DataFrame with a table of drawdowns
        '''
        self._make_sure_has_run()
        if target == "strategy":
            series = self._df['strategy_last'].dropna() 
        else:
            series = self._df['last'].dropna() 
        xs = np.round(np.array(series.values),5)
        ds = series.index
        dds = self._max_dd(xs, ds)
        dds.sort()
        dds = dds[::-1]

        df = pd.DataFrame(dds,columns =['dd', 'high', 'low', 'highd', 'lowd'])
        df['days'] = (df['lowd'] - df['highd'])
        recoveryd = []
        for index, row in df.iterrows():
            try:
                temp = series.loc[row['lowd']:]
                recoveryd.append(temp[temp > row['high']].index[0])
            except:
                recoveryd.append(series.index[-1]) # has not recovered yet, use "todays" date
                continue
        df['recoveryd'] = recoveryd
        df['rdays'] = df['recoveryd'] - df['lowd']
        return df[df['dd'] >= cutoff]


    def _trade_logic(self):
        '''Implements the trade logic in order to come up with
        a set of stances
        '''

        if self._ema:
            self._df['ms'] = np.round(self._df['last'].ewm(span=self._ms, adjust=False).mean(),8)
            self._df['ml'] = np.round(self._df['last'].ewm(span=self._ml, adjust=False).mean(),8)
        else:
            self._df['ms'] = np.round(self._df['last'].rolling(window=self._ms).mean(), 8)
            self._df['ml'] = np.round(self._df['last'].rolling(window=self._ml).mean(), 8)

        self._df['mdiff'] = self._df['ms'] - self._df['ml']
        self._df['stance'] = np.where(self._df['mdiff'] >= 0, 1, 0)

        if not self._long_only:
            self._df['stance'] = np.where(self._df['mdiff'] < 0, -1, self._df['stance'])
            self._df['stance'].replace(to_replace=0, method='ffill').values


    def _run(self):
        """
        Runs the strategy and calculates returns and performance
        This only gets run when needed on a lazy basis
        """

        self._trade_logic()

        self._df['market'] = np.log(self._df['last'] / self._df['last'].shift(1))

        self._df['buy'] = np.where( (self._df['stance'] != self._df['stance'].shift(1)) & (self._df['stance'] == 1), self._df['last'], np.NAN)

        if not self._long_only:
            self._df['sell'] = np.where( (self._df['stance'] != self._df['stance'].shift(1)) & (self._df['stance'] == -1), self._df['last'], np.NAN)
        else:
            self._df['sell'] = np.where( (self._df['stance'] != self._df['stance'].shift(1)) & (self._df['stance'] == 0), self._df['last'], np.NAN)

        self._df['strategy'] = self._df['market'] * self._df['stance'].shift(1) #shift(1) means day before
        self._df['strategy_last'] = self._df['strategy'].cumsum().apply(np.exp).dropna()

        #years = len(self._df) / 365.25
        start_date, end_date = self._df.index[0], self._df.index[-1]
        years = (end_date - start_date).days / 365.25

        self._df['trade'] = np.where(self._df['stance'] != self._df['stance'].shift(1), 1, 0)
        trades = self._df['trade'].sum()
        market = ((np.exp(self._df['market'].cumsum()[-1]) - 1) * 100)
        market_pa = ((market / 100 + 1) ** (1 / years) - 1) * 100
        strategy = ((np.exp(self._df['strategy'].cumsum()[-1]) - 1) * 100)
        strategy_pa = ((strategy / 100 + 1) ** (1 / years) - 1) * 100
        sharpe = math.sqrt(len(self._df)) * np.average(self._df['strategy'].dropna()) / np.std(self._df['strategy'].dropna())
        self._results = {"Strategy":np.round(strategy,2), "Market":np.round(market,2),"Trades":trades,"Sharpe":np.round(sharpe,2),
                        "Strategy_pa": np.round(strategy_pa,2), "Market_pa": np.round(market_pa,2), "Years": np.round(years,2)}
        self._has_run = True

