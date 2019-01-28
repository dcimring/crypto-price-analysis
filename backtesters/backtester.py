'''Abstract class for backtesting strategies. Takes a vectorised approach using Pandas and Numpy.
'''

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.core.debugger import set_trace

class Backtester(object):
    '''Abstract base class

    Parameters:
    series: (Panda Series) a list of CLOSE prices by date
    long_only: (boolean) True if the strategy can only go long
    '''

    def __init__(self, series, long_only=False, slippage=0):
        self._df = series.to_frame().dropna()
        self._df.columns = ['last']
        self._long_only = long_only
        self._results = {}
        self._has_run = False
        self._start_date = self._df.index[0].strftime('%Y-%m-%d')
        self._end_date = self._df.index[-1].strftime('%Y-%m-%d')
        self._slippage = slippage

    def change_data(self, series):
        '''Allow the price data to be changed after the strategy is initialised'''
        self._df = series.to_frame().dropna()
        self._df.columns = ['last']
        self._results = {}
        self._has_run = False
        self._start_date = self._df.index[0].strftime('%Y-%m-%d')
        self._end_date = self._df.index[-1].strftime('%Y-%m-%d')

    def __str__(self):
        '''Each concreate class will have its own string representation
        '''
        pass

    def _make_sure_has_run(self):
        if not self._has_run:
            self._run()

    def results(self):
        self._make_sure_has_run()
        return self._results


    def _sum_returns(self, returns, groupby):
        '''
        Returns must be log returns
        '''
        return np.exp(returns.groupby(groupby).sum()) - 1

    def _cross_over (self, a, b):
        '''Returns true where series a crosses over series b'''
        return ( (a > b) & (a.shift(1) < b.shift(1) ) ) 

    def _cross_under (self, a, b):
        '''Returns true where series a crosses over series b'''
        return ( (a < b) & (a.shift(1) > b.shift(1) ) ) 


    def trades(self):
        '''Return a Pandas DataFrame with details of each trade
        '''
        self._make_sure_has_run()
        buy = self._df['buy'].dropna()
        sell = self._df['sell'].dropna()
        r = []
        
        for date, price in buy.iteritems(): # long trades
            
            # if you buy but stance is 0 or less then it was a short cover not a new long
            if self._df.loc[date,'stance']<=0:
                continue 
            
            try:
                sell_price = sell.loc[date:][0] # find next sell
                sell_date = sell.loc[date:].index[0] # and the date sold 
            except IndexError: # its the end of the time series
                sell_price = self._df['last'].iloc[-1] # current price
                sell_date = self._df['last'].index[-1] # current date
            finally:
                days = (sell_date - date).days 
                r.append((date,"Long",round(price,6),round(sell_price,6),days,sell_price/price-1))   

        if not self._long_only: # short trades

            for date, price in sell.iteritems():

                # if you sell but stance is 0 or more then it was sale not a new short
                if self._df.loc[date,'stance']>=0:
                    continue 

                try:
                    cover_price = buy.loc[date:][0] # find next buy
                    cover_date = buy.loc[date:].index[0] # and the date  
                except IndexError: # its the end of the time series
                    cover_price = self._df['last'].iloc[-1] # current price
                    cover_date = self._df['last'].index[-1] # current date
                finally:
                    days = (cover_date - date).days #todo - does this need +1?
                    r.append((date,"Short",round(price,6),round(cover_price,6),days,price/cover_price-1))  

        df = pd.DataFrame(sorted(r, key = lambda x: x[0]))
        df.columns = ['Date','Type','Entry','Exit','Days','Return%']
        df['Return%'] = np.round(df['Return%'] * 100,2)
        df.set_index('Date', inplace=True)

        return df

    def plot(self, start_date=None, end_date=None, figsize=None, ax=None):
        '''Plot of prices and the the buy and sell points
        Stratgies can add their own additional indicators
        '''
        self._make_sure_has_run()
        temp = self._df.loc[start_date:end_date]
       
        if not ax:
            fig, ax = plt.subplots(figsize=figsize)

        ax.plot(temp['last'], label='Price')
        ax.plot(temp['buy'],color='g', linestyle='None', marker='^')
        ax.plot(temp['sell'],color='r', linestyle='None', marker='v')
        
        return ax

    def plot_equity_curve(self, start_date=None, end_date=None, figsize=None):
        '''Plot an equity curve for the strategy versus
        the market'''
        self._make_sure_has_run()
        self._df[['market','strategy']].loc[start_date:end_date].cumsum().apply(np.exp).plot(figsize=figsize)

    def plot_heatmap(self, target="strategy", figsize=None):
        '''Draw a heatmap of returns

        Parameters:
        target: (string) "strategy" or "market" or "relative"
        "relative" shows the compound difference and not the arithmetic difference
        e.g. compound difference between 50% and -50% is (1+0.5)/(1-0.5)-1 = 1.5/0.5-1 = 2 = 200%

        Returns:
        None
        '''
        self._make_sure_has_run()
        if target == "strategy":
            returns = self._df['strategy'].copy()
        elif target == "market":
            returns = self._df['market'].copy()
        else:
            returns = (self._df['strategy']-self._df['market']).copy()
        original_returns = returns.copy()
        returns_index = returns.resample('MS').first().index
        returns_values = self._sum_returns(returns, (returns.index.year, returns.index.month)).values
        #set_trace()
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
        ax.set_title("Monthly Returns %s (%%)\n" % target.capitalize(), fontsize=14, color="black", fontweight="bold")
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
        '''Each concrete class will implement the trade logic here in order to come up with
        a set of stances
        '''
        self._df['stance'] = 1 # Default strategy is buy and hold

    def _market_returns(self):

        self._df['market'] = np.log(self._df['last'] / self._df['last'].shift(1))

        # For buy, sell, and trade calculation shift(1) leads to a value of NA for first entry which then differs from 0
        # This was fixed by doing a fillna(0) after the shift(1)

        self._df['buy'] = np.where( self._df['stance'] - self._df['stance'].shift(1).fillna(0) > 0, self._df['last'], np.NAN)
        self._df['sell'] = np.where( self._df['stance'] - self._df['stance'].shift(1).fillna(0) < 0, self._df['last'], np.NAN)


    def _run(self):
        """
        Runs the strategy and calculates returns and performance
        This only gets run when needed on a lazy basis
        """

        if self._has_run:
            return

        self._trade_logic()
        self._market_returns()

        # apply slippage
        # If I trade today and stance == 1 then reduce market return 
        self._df['trade'] = np.where(self._df['stance'] != self._df['stance'].shift(1).fillna(0), 1, 0)
        self._df['trade_size'] = np.abs(self._df['stance'] - self._df['stance'].shift(1).fillna(0))
        self._df['market_adj'] = self._df['market'] - (self._df['trade_size'].shift(1) * self._slippage * self._df['stance'].shift(1))       

        # If I get a buy trigger today then I can buy at todays close (tomorrow's open) and thus get tomorrow's return

        self._df['strategy'] = self._df['market_adj'] * self._df['stance'].shift(1) #shift(1) means day before
        self._df['strategy_last'] = self._df['strategy'].cumsum().apply(np.exp).dropna()

        # since we are using log returns multiplying by -1 for shorts works

        start_date, end_date = self._df.index[0], self._df.index[-1]
        years = (end_date - start_date).days / 365.25
        
        trades = self._df['trade'].sum()
        market = ((np.exp(self._df['market'].cumsum()[-1]) - 1) * 100)
        market_pa = ((market / 100 + 1) ** (1 / years) - 1) * 100
        strategy = ((np.exp(self._df['strategy'].cumsum()[-1]) - 1) * 100)
        strategy_pa = ((strategy / 100 + 1) ** (1 / years) - 1) * 100

        # Calculating sharpe using log returns
        # For daily data you annualise with sqrt(365.25)
        # Work out how many periods per year

        days = (self._df.index[1] - self._df.index[0]).days
        secs = (self._df.index[1] - self._df.index[0]).seconds
        periods_per_year = 365.25 / (days + secs / 3600.0 / 24.0)

        sharpe = math.sqrt(periods_per_year) * np.average(self._df['strategy'].dropna()) / np.std(self._df['strategy'].dropna())
        market_sharpe = math.sqrt(periods_per_year) * np.average(self._df['market'].dropna()) / np.std(self._df['market'].dropna())

        # Current trade unrealised profit or loss
        current_stance = self._df['stance'].iloc[-1]
        last = self._df['last'].iloc[-1]
        if current_stance == 1:
            entry = self._df['buy'].dropna()[-1]
            unrealised = (last / entry - 1) * 100
        elif current_stance == -1:
            entry = self._df['sell'].dropna()[-1]
            unrealised = (entry / last - 1) * 100
        else:
            unrealised = 0

        if 0 in self._df.stance.value_counts().index:
            time_in_market = 1 - float(self._df.stance.value_counts()[0]) / float(self._df.stance.count())
        else:
            time_in_market = 1

        time_in_market = np.round(time_in_market * 100, 2)

        self._results = {"Strategy":np.round(strategy,2), "Market":np.round(market,2),"Trades":trades,"Sharpe":np.round(sharpe,2),
                        "Strategy_pa": np.round(strategy_pa,2), "Market_pa": np.round(market_pa,2), "Years": np.round(years,2),
                        "Trades_per_month":np.round(trades/years/12,2),"Market_sharpe":np.round(market_sharpe,2),
                        'Current_stance':current_stance,"Unrealised":np.round(unrealised,2),'Time_in_market':time_in_market}
        self._has_run = True

