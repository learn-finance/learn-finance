import datetime
import pandas as pd
import yfinance as yf
from pandas_datareader import data as pdr
import numpy as np
import matplotlib.pyplot as plt
src = "C:/Users/prasa/PycharmProjects/PortfolioResearch/"
start = '2000-12-31'
end = datetime.date.today().strftime('%Y-%m-%d')
yf.pdr_override()


class SignalResearch:
    symbol_df = pd.read_excel(src + 'universe.xlsx', sheet_name='high_low', index_col=[0])
    tickers = symbol_df.index.tolist()

    def __init__(self):
        self.yahoo_data = pdr.get_data_yahoo(self.tickers, start=start, end=end)

    def nperiod_signal(self, trade_signal, nper=252, horizon=5):

        returns_dict = {}
        win_rate=[]
        realized_ret = []
        realized_risk = []
        for symbol in self.tickers:
            adj_close = self.yahoo_data['Adj Close', symbol].copy()

            if trade_signal == 'high':
                nper_signal = adj_close.rolling(window=nper).apply(max)
            else:
                nper_signal = adj_close.rolling(window=nper).apply(min)

            adj_start = nper_signal.dropna().index[0]
            trade_df = pd.DataFrame(index=nper_signal.index)
            position = 0
            trade_count = 1
            closing_counter = 0
            for counter in range(len(nper_signal)):
                px = adj_close.iloc[counter]
                hi_lo = nper_signal.iloc[counter]

                if pd.isna(hi_lo):
                    trade_df.loc[trade_df.index[counter], 'Trades'] = 'No Trade'
                    trade_df.loc[trade_df.index[counter], 'Entry'] = 0
                    trade_df.loc[trade_df.index[counter], 'Exit'] = 0
                    trade_df.loc[trade_df.index[counter], 'ClosingPx'] = 0
                    trade_df.loc[trade_df.index[counter], 'Returns'] = np.nan
                    trade_df.loc[trade_df.index[counter], 'HPR'] = 0.0
                    trade_df.loc[trade_df.index[counter], 'Comment'] = 'No Open Trades'
                    position = 0

                elif px == hi_lo and position == 0:
                    trade_df.loc[trade_df.index[counter], 'Trades'] = 'Position Open'
                    buy_px = adj_close.iloc[counter]
                    trade_df.loc[trade_df.index[counter], 'Entry'] = 1
                    trade_df.loc[trade_df.index[counter], 'Exit'] = 0
                    trade_df.loc[trade_df.index[counter], 'ClosingPx'] = px
                    trade_df.loc[trade_df.index[counter], 'Returns'] = np.nan
                    trade_df.loc[trade_df.index[counter], 'HPR'] = 0.0
                    trade_df.loc[trade_df.index[counter], 'Comment'] = f"Opened trade #{trade_count}"
                    closing_counter = counter + horizon
                    position = 1

                elif counter < closing_counter and position == 1:
                    trade_df.loc[trade_df.index[counter], 'ClosingPx'] = px
                    trade_df.loc[trade_df.index[counter], 'Returns'] = adj_close.iloc[counter] \
                                                                       / adj_close.iloc[counter - 1] - 1

                elif counter == closing_counter and position == 1:
                    trade_df.loc[trade_df.index[counter], 'Trades'] = 'Position Closed'
                    trade_df.loc[trade_df.index[counter], 'Exit'] = 1
                    trade_df.loc[trade_df.index[counter], 'ClosingPx'] = px
                    trade_df.loc[trade_df.index[counter], 'Comment'] = f"Closed trade #{trade_count}"
                    trade_df.loc[trade_df.index[counter], 'Returns'] = adj_close.iloc[counter] \
                                                                       / adj_close.iloc[counter - 1] - 1
                    trade_df.loc[trade_df.index[counter], 'HPR'] = adj_close.iloc[counter] / buy_px - 1
                    position = 0
                    buy_px = 0.0
                    trade_count +=1

                else:
                    position == position
                    trade_df.loc[trade_df.index[counter], 'Returns'] = np.nan

            hpr_return = trade_df[trade_df.HPR!=0].HPR.dropna()
            gt_zero = hpr_return>0
            win_rate.append(gt_zero.sum()/gt_zero.count())
            realized_ret.append(gt_zero.mean() * len(gt_zero))
            realized_risk.append(gt_zero.std() * np.sqrt(len(gt_zero)))
            returns_dict.update({symbol:trade_df.Returns})
            pd.DataFrame(returns_dict).dropna().describe().loc['std'] * np.sqrt(250)
            pd.DataFrame(returns_dict).dropna().describe().loc['mean'] * np.sqrt(250)


        # startegy_return = trade_df.Returns
        #
        # buy_hold_return = adj_close.loc[:, adj_close.columns[0]].resample('Y', closed='right').last().pct_change()

        print('test')


if __name__ == "__main__":
    objSignal = SignalResearch()
    objSignal.nperiod_signal('low', 252, 90)
