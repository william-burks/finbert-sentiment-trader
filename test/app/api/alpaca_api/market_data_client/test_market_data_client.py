import pytest
from flask import Flask
from flask_restx import Api
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import pandas as pd
from app.api.alpaca_api.alpaca_client import AlpacaClient
from app.api.alpaca_api.market_data_client import api as market_data_api, GetBars, GetLatestBar, GetAsset  # Replace 'your_module' with the actual module name

@pytest.fixture
def client():
    app = Flask(__name__)
    api = Api(app)
    api.add_namespace(market_data_api)
    return app.test_client()

@pytest.fixture
def mock_alpaca_client():
    with patch.object(AlpacaClient, 'get_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        yield mock_client

class TestGetBars:
    def test_get_bars_success(self, client, mock_alpaca_client):
        mock_df = pd.DataFrame({
            'timestamp': [datetime(2023, 1, 1, tzinfo=timezone.utc)],
            'open': [100],
            'high': [101],
            'low': [99],
            'close': [100.5],
            'volume': [1000],
            'trade_count': [50],
            'vwap': [100.2]
        })
        mock_alpaca_client.get_bars.return_value.df = mock_df

        response = client.get('/Market Data/get_bars/AAPL/1D/2023-01-01/2023-01-02')

        assert response.status_code == 200
        data = response.get_json()
        assert data['asset'] == 'AAPL'
        assert len(data['data']) == 1
        assert 'timestamp' in data['data'][0]
        assert 'bars' in data['data'][0]
        assert len(data['data'][0]['bars']) == 1

    def test_get_bars_error(self, client, mock_alpaca_client):
        mock_alpaca_client.get_bars.side_effect = Exception('API Error')

        response = client.get('/Market Data/get_bars/AAPL/1D/2023-01-01/2023-01-02')

        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

class TestGetLatestBar:
    def test_get_latest_bar_success(self, client, mock_alpaca_client):
        mock_bar = Mock(
            timestamp=datetime(2023, 1, 1, tzinfo=timezone.utc),
            close=100.5,
            high=101,
            low=99,
            trade_count=50,
            open=100,
            volume=1000,
            vwap=100.2
        )
        mock_alpaca_client.get_latest_bar.return_value = mock_bar

        response = client.get('/Market Data/get_latest_bar/AAPL')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        timestamp = list(data.keys())[0]
        assert '2023-01-01' in timestamp
        assert data[timestamp]['close'] == 100.5

    def test_get_latest_bar_error(self, client, mock_alpaca_client):
        mock_alpaca_client.get_latest_bar.side_effect = Exception('API Error')

        response = client.get('/Market Data/get_latest_bar/AAPL')

        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

class TestGetAsset:
    def test_get_asset_success(self, client, mock_alpaca_client):
        mock_asset = {
            'id': 'asset_id',
            'asset_class': 'us_equity',
            'exchange': 'NASDAQ',
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'status': 'active',
            'tradable': True,
            'marginable': True,
            'shortable': True,
            'easy_to_borrow': True,
            'fractionable': True,
            'attributes': ['attr1', 'attr2'],
            'margin_requirement_long': '30',
            'margin_requirement_short': '30',
            'maintenance_margin_requirement': 25.0
        }
        mock_alpaca_client.get_asset.return_value = mock_asset

        response = client.get('/Market Data/get_asset/AAPL')

        assert response.status_code == 200
        data = response.get_json()
        print(f"Response data: {data}")  # Add this line for debugging
        assert data['id'] == 'asset_id'
        assert data['class'] == 'us_equity'
        assert data['symbol'] == 'AAPL'
        assert data['attributes'] == ['attr1', 'attr2']

    def test_get_asset_error(self, client, mock_alpaca_client):
        mock_alpaca_client.get_asset.side_effect = Exception('API Error')

        response = client.get('/Market Data/get_asset/AAPL')

        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

    def test_get_asset_missing_attributes(self, client, mock_alpaca_client):
        mock_asset = Mock(spec=[])  # Create a mock with no attributes
        mock_alpaca_client.get_asset.return_value = mock_asset

        response = client.get('/Market Data/get_asset/AAPL')

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 'N/A'
        assert data['class'] == 'N/A'
        assert data['attributes'] == []