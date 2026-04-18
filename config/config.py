import os
from dotenv import load_dotenv
from lumibot.brokers import Alpaca

# Load environment variables from .env file
load_dotenv()

# Alpaca API credentials
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')


# Capital Type
PAPER = True
CASH = False


# Alpaca API URL
BASE_URL = os.getenv('ALPACA_BASE_URL')

BROKER = Alpaca(
    {"API_KEY": API_KEY,
     "API_SECRET": API_SECRET,
     "PAPER": PAPER,
     "BASE_URL": BASE_URL}
)

# Trading parameters
DEFAULT_SYMBOL = 'SPY'
CASH_AT_RISK = 0.5

# Technical Analysis parameters
TA_TIMEFRAME = '1Hour'
TA_DAYS = 30

# Sentiment Analysis parameters
SENTIMENT_DAYS = 3
SENTIMENT_THRESHOLD = 0.999

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'trading_log.txt'

# Ensure all required environment variables are set
required_env_vars = ['ALPACA_API_KEY', 'ALPACA_API_SECRET']
for var in required_env_vars:
    if os.getenv(var) is None:
        raise ValueError(f"Required environment variable {var} is not set")