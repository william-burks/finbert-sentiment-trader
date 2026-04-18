# app/api/strategy_init.py

from app.trader.trader import MLTrader
from config.config import BROKER, DEFAULT_SYMBOL, CASH_AT_RISK

class StrategyInit:
    strategy = None

    @classmethod
    def initialize_strategy(cls):
        cls.strategy = MLTrader(
            name='api_strategy',
            broker=BROKER,
            parameters={"symbol": DEFAULT_SYMBOL, "cash_at_risk": CASH_AT_RISK}
        )
        return cls.strategy