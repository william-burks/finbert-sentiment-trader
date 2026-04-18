import pytest
from flask import Flask
from flask_restx import Api
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from app.api.alpaca_api.alpaca_client import AlpacaClient
from app.api.alpaca_api.news_client import api as news_api, GetNews  # Replace 'your_module' with the actual module name

@pytest.fixture
def client():
    app = Flask(__name__)
    api = Api(app)
    api.add_namespace(news_api)
    return app.test_client()

@pytest.fixture
def mock_alpaca_client():
    with patch.object(AlpacaClient, 'get_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        yield mock_client

class TestGetNews:
    def test_get_news_success(self, client, mock_alpaca_client):
        mock_news_item = Mock(
            id='1234',
            headline='Test Headline',
            author='Test Author',
            created_at=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2023, 1, 2, tzinfo=timezone.utc),
            summary='Test Summary',
            url='http://test.com',
            symbols=['AAPL'],
            source='Test Source'
        )
        mock_alpaca_client.get_news.return_value = [mock_news_item]

        response = client.get('/News/get_news/AAPL/2023-01-01/2023-01-02')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['id'] == '1234'
        assert data[0]['headline'] == 'Test Headline'
        assert data[0]['created_at'] == '2023-01-01T00:00:00+00:00'
        assert data[0]['updated_at'] == '2023-01-02T00:00:00+00:00'

    def test_get_news_invalid_start_date(self, client, mock_alpaca_client):
        response = client.get('/News/get_news/AAPL/invalid-date/2023-01-02')

        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'Invalid date format' in data['message']

    def test_get_news_invalid_end_date(self, client, mock_alpaca_client):
        response = client.get('/News/get_news/AAPL/2023-01-01/invalid-date')

        assert response.status_code == 400
        data = response.get_json()
        assert 'message' in data
        assert 'Invalid date format' in data['message']

    def test_get_news_api_error(self, client, mock_alpaca_client):
        mock_alpaca_client.get_news.side_effect = Exception('API Error')

        response = client.get('/News/get_news/AAPL/2023-01-01/2023-01-02')

        assert response.status_code == 500
        data = response.get_json()
        assert 'message' in data
        assert 'An error occurred: API Error' in data['message']

    def test_get_news_string_datetime(self, client, mock_alpaca_client):
        mock_news_item = Mock(
            id='1234',
            headline='Test Headline',
            author='Test Author',
            created_at='2023-01-01T00:00:00Z',  # String instead of datetime
            updated_at='2023-01-02T00:00:00Z',  # String instead of datetime
            summary='Test Summary',
            url='http://test.com',
            symbols=['AAPL'],
            source='Test Source'
        )
        mock_alpaca_client.get_news.return_value = [mock_news_item]

        response = client.get('/News/get_news/AAPL/2023-01-01/2023-01-02')

        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['created_at'] == '2023-01-01T00:00:00Z'
        assert data[0]['updated_at'] == '2023-01-02T00:00:00Z'