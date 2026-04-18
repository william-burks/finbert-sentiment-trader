# import pandas as pd
# import pandas_ta as ta
# import numpy as np
# from datetime import datetime, timedelta
# import pytz
# from app.api.market_data import MarketData
#
# class ScalpingAnalysis:
#     def __init__(self):
#         self.market_data = MarketData()
#         self.data_cache = {}
#         self.last_fetch_time = {}
#
#     def get_historical_data(self, symbol, days=30):
#         current_time = datetime.now(pytz.UTC)
#         fifteen_minutes_ago = current_time - timedelta(minutes=15)
#         end_date = min(current_time, fifteen_minutes_ago)
#         start_date = end_date - timedelta(days=days)
#
#         df = self.market_data.get_bars(symbol, "1Hour", start_date, end_date)
#         df = df[df.high != df.low]
#
#         # Update the cache
#         self.data_cache[symbol] = df
#         self.last_fetch_time[symbol] = current_time
#
#         return self._analyze_data(df)
#
#     def _analyze_data(self, df):
#         df["EMA_slow"] = ta.ema(df.close, length=50)
#         df["EMA_fast"] = ta.ema(df.close, length=30)
#         df["RSI"] = ta.rsi(df.close, length=10)
#         df["ATR"] = ta.atr(df.high, df.low, df.close, length=7)
#
#         my_bbands = ta.bbands(df.close, length=15, std=1.5)
#         df = df.join(my_bbands)
#
#         return df
#
#     def get_ema_signal(self, df, current_candle, backcandles):
#         start = max(0, df.index.get_loc(current_candle) - backcandles)
#         end = df.index.get_loc(current_candle) + 1
#         relevant_rows = df.iloc[start:end]
#
#         if all(relevant_rows["EMA_fast"] < relevant_rows["EMA_slow"]):
#             return 1
#         elif all(relevant_rows["EMA_fast"] > relevant_rows["EMA_slow"]):
#             return 2
#         return 0
#
#     def get_total_signal(self, df, current_candle, backcandles):
#         ema_signal = self.get_ema_signal(df, current_candle, backcandles)
#
#         if ema_signal == 2 and df.loc[current_candle, 'close'] <= df.loc[current_candle, 'BBL_15_1.5']:
#             return 2
#         if ema_signal == 1 and df.loc[current_candle, 'close'] >= df.loc[current_candle, 'BBU_15_1.5']:
#             return 1
#         return 0
#
#     def analyze(self, df):
#         df['EMASignal'] = df.apply(lambda row: self.get_ema_signal(df, row.name, 7), axis=1)
#         df['TotalSignal'] = df.apply(lambda row: self.get_total_signal(df, row.name, 7), axis=1)
#         return df