from venv import logger
from alpaca_trade_api import REST
from config.config import API_KEY, API_SECRET, BASE_URL

class AlpacaClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AlpacaClient, cls).__new__(cls)
            cls._instance.client = None
        return cls._instance

    def __init__(self):
        if self.client is None:
            logger.info(BASE_URL)
            self.client = REST(API_KEY, API_SECRET, BASE_URL)

    def get_client(self):
        return self.client