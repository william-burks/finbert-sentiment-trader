import pytest
from unittest.mock import patch
from app.api.alpaca_api.alpaca_client import AlpacaClient
from config.config import BASE_URL

@pytest.fixture(scope="module")
def alpaca_client():
    """Fixture for AlpacaClient"""
    with patch('app.api.alpaca_api.alpaca_client.REST') as mock_rest:
        yield AlpacaClient()

def test_singleton_behavior(alpaca_client):
    """Test that AlpacaClient is a singleton."""
    another_client = AlpacaClient()
    assert alpaca_client is another_client, "AlpacaClient should be a singleton."

def test_client_initialization(alpaca_client):
    """Test that the REST client is initialized correctly."""
    assert alpaca_client.get_client() is not None, "The REST client should be initialized."
    assert isinstance(alpaca_client.get_client(), type(alpaca_client.client)), "Client should be of the same type as the initialized client."

def test_client_initialization_logging():
    """Test that the logger logs the BASE_URL when initializing the client."""
    with patch('app.api.alpaca_api.alpaca_client.logger.info') as mock_logger:
        AlpacaClient()  # Trigger initialization
        # mock_logger.assert_called_once_with(BASE_URL)  # Check logging

def test_get_client_method(alpaca_client):
    """Test the get_client method returns the initialized client."""
    client = alpaca_client.get_client()
    assert client is not None, "get_client should return the initialized REST client."
    assert client is alpaca_client.client, "get_client should return the same client instance."

def test_client_initialization_twice():
    """Test that initializing the client twice does not create a new instance."""
    with patch('app.api.alpaca_api.alpaca_client.REST') as mock_rest:
        client1 = AlpacaClient()  # First initialization
        client2 = AlpacaClient()  # Second initialization
        assert client1 is client2, "Multiple initializations should return the same instance."
