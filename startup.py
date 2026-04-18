import logging
import threading
import time

from flask import Flask
from datetime import datetime
from flask_restx import Api
from lumibot.backtesting import YahooDataBacktesting
from app.api.alpaca_api.account_client import api as account_client
from app.api.alpaca_api.news_client import api as news_client
from app.api.alpaca_api.market_data_client import api as market_data_client
from app.api.strategy_client import api as strategy_api
from app.api.orders_client import api as orders_api
from app.api.strategy_init import StrategyInit
from app.api.alpaca_api.alpaca_client import AlpacaClient
from config import LOG_LEVEL, LOG_FILE, DEFAULT_SYMBOL, CASH_AT_RISK
from werkzeug.serving import run_simple

startup = Flask(__name__)
app = startup
alpaca_api = AlpacaClient
api = Api(app)

# Set up logging
logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE, filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

api.add_namespace(account_client, path='/account')
api.add_namespace(news_client, path='/news')
api.add_namespace(market_data_client, path='/market_data')
api.add_namespace(strategy_api, path='/strategy')
api.add_namespace(orders_api, path='/orders')

def run_flask():
    run_simple('0.0.0.0', 5000, app, use_reloader=False, use_debugger=True)

def backtest_trader():
    # Define trading parameters
    symbol = DEFAULT_SYMBOL
    cash_at_risk = CASH_AT_RISK
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2023, 12, 31)

    logger.info(f"Running backtest from {start_date} to {end_date}")
    run_backtest(start_date, end_date, symbol, cash_at_risk)

def run_backtest(start_date, end_date, symbol, cash_at_risk):
    """Run a backtest for the given strategy and parameters."""
    StrategyInit.initialize_strategy().strategy.backtest(
        YahooDataBacktesting,
        start_date,
        end_date,
        parameters={"symbol": "SPY", "cash_at_risk": cash_at_risk}
    )

if __name__ == "__main__":

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    time.sleep(2)

    # Press enter to begin the backtest
    start = input("Press 'Enter' or 'Return' to begin the trading backtest: ")
    logger.info("Starting trading application")
    backtest_trader()
    logger.info("Backtest completed")

    # Keep the main thread alive to allow Flask to continue running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logger.info("Application terminated by user")