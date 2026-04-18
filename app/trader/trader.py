import os
from datetime import timedelta, datetime

from alpaca_trade_api import REST
from lumibot.strategies.strategy import Strategy

from app.util.sentiment_analysis.finbert import estimate_sentiment

class MLTrader(Strategy):
    def initialize(self, symbol: str = "SYP", cash_at_risk: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.alpaca_rest_api = REST(
            key_id=os.getenv('ALPACA_API_KEY'),
            secret_key=os.getenv('ALPACA_API_SECRET'),
            base_url=os.getenv('ALPACA_BASE_URL'))

    def position_sizing(self, cash=None, last_price=None):
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return quantity

    def get_dates(self):
        today = self.get_datetime()
        minus_three_days = today - timedelta(days=3)
        return today.strftime("%Y-%m-%d"), minus_three_days.strftime("%Y-%m-%d")

    def get_sentiment(self, today, three_days_ago):
        news = self.alpaca_rest_api.get_news(symbol=self.symbol, start=three_days_ago, end=today)
        headlines = [item.__dict__["_raw"]["headline"] for item in news] # Dict of headlines
        symbols = [item.__dict__["_raw"]["symbols"] for item in news] # Dict of referenced symbols

        # Flatten the list and remove duplicate symbols
        symbols = list(set(symbol for sublist in symbols for symbol in sublist))

        probability, sentiment = estimate_sentiment(headlines)
        return probability, sentiment

    def execute_trade(self, sentiment, probability, last_price, quantity):
        print("Sentiment: ", sentiment)
        if sentiment == "positive" and probability > 0.999:
            self._execute_buy(last_price, quantity)
        elif sentiment == "negative" and probability > 0.999:
            self._execute_sell(last_price, quantity)

    def _execute_buy(self, last_price, quantity):
        if self.last_trade == "sell":
            self.sell_all()

        # Creating and submitting a new order with Strategy API
        order = self.create_order(
            self.symbol,
            quantity,
            "buy",
            take_profit_price=last_price * 1.20,  # Setting a take profit 20% above the purchase price
            stop_loss_price=last_price * 0.95,  # Setting a stop loss 5% below the purchase price
        )
        self.submit_order(order)
        self.last_trade = "buy"

    def _execute_sell(self, last_price, quantity):
        if self.last_trade == "buy":
            self.sell_all()

        # Creating and submitting a new order with Strategy API
        order = self.create_order(
            self.symbol,
            quantity,
            "sell",
            take_profit_price=last_price * 0.80,  # Setting a take profit 20% above the purchase price
            stop_loss_price=last_price * 1.05,  # Setting a stop loss 5% below the purchase price
        )
        self.submit_order(order)
        self.last_trade = "sell"



    def on_trading_iteration(self):

        today, three_days_ago = self.get_dates()
        probability, sentiment = self.get_sentiment(today, three_days_ago)  # Get the sentiment for the current trade

        cash = self.get_cash()  # Get the current capital available
        print()
        print("Cash: ", cash)
        last_price = self.get_last_price(self.symbol)  # Get the last price on the current symbol
        quantity = self.position_sizing(cash, last_price)  # Get position sizing before executing a trade


        if cash > last_price:  # Check if there is enough cash to perform a transaction
            self.execute_trade(sentiment, probability, last_price, quantity)

