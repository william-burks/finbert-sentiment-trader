import pytest
from flask import Flask
from flask_restx import Api
from unittest.mock import Mock, patch
from alpaca_trade_api.rest import APIError
from app.api.alpaca_api.alpaca_client import AlpacaClient
from app.api.alpaca_api.account_client import api as account_api, GetAccount, GetCash, \
    account_to_dict  # Replace 'your_module' with the actual module name


@pytest.fixture
def client():
    app = Flask(__name__)
    api = Api(app)
    api.add_namespace(account_api)
    return app.test_client()


@pytest.fixture
def mock_alpaca_client():
    with patch.object(AlpacaClient, 'get_client') as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        yield mock_client


def test_get_account_success(client, mock_alpaca_client):
    mock_account = Mock(
        account_blocked=False,
        account_number='123456789',
        cash='5000.00',
        accrued_fees='0.00',
        balance_asof='2023-09-20T14:30:00Z',
        bod_dtbp='10000.00',
        buying_power='10000.00',
        created_at='2023-01-01T00:00:00Z',
        crypto_status='active',
        crypto_tier='tier_2',
        currency='USD',
        daytrade_count=0,
        daytrading_buying_power='20000.00',
        effective_buying_power='10000.00',
        equity='15000.00',
        id='account_id',
        initial_margin='7500.00',
        intraday_adjustments='0.00',
        last_equity='14500.00',
        last_maintenance_margin='3750.00',
        long_market_value='10000.00',
        maintenance_margin='3750.00',
        multiplier=2,
        non_marginable_buying_power='5000.00',
        options_approved_level='level_2',
        options_buying_power='10000.00',
        options_trading_level='level_2',
        pattern_day_trader=False,
        pending_reg_taf_fees='0.00',
        portfolio_value='15000.00',
        position_market_value='10000.00',
        regt_buying_power='10000.00',
        short_market_value='0.00',
        shorting_enabled=True,
        sma='7500.00',
        status='ACTIVE',
        trade_suspended_by_user=False,
        trading_blocked=False,
        transfers_blocked=False,
    )
    mock_alpaca_client.get_account.return_value = mock_account

    response = client.get('/Account/get_account')

    assert response.status_code == 200
    data = response.get_json()
    assert data['account_number'] == '123456789'
    assert data['cash'] == '5000.00'
    # Add assertions for other attributes


def test_get_account_unauthorized(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = APIError({"message": "Unauthorized"})

    response = client.get('/Account/get_account')

    assert response.status_code == 401
    data = response.get_json()
    assert 'Unauthorized: Invalid API key' in data['message']

def test_get_account_bad_request(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = APIError({"message": "Bad request"})

    response = client.get('/Account/get_account')

    assert response.status_code == 400
    data = response.get_json()
    assert 'Bad request' in data['message']


def test_get_account_api_error(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = APIError({"message": "API error"}, 500)

    response = client.get('/Account/get_account')

    assert response.status_code == 500
    data = response.get_json()
    assert 'Alpaca API error' in data['message']


def test_get_account_unexpected_error(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = Exception("Unexpected error")

    response = client.get('/Account/get_account')

    assert response.status_code == 500
    data = response.get_json()
    assert 'An unexpected error occurred' in data['message']


def test_get_cash_success(client, mock_alpaca_client):
    mock_account = Mock(cash='5000.00')
    mock_alpaca_client.get_account.return_value = mock_account

    response = client.get('/Account/get_cash')

    assert response.status_code == 200
    data = response.get_json()
    assert data['Cash'] == '5000.00'


def test_get_cash_unauthorized(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = APIError({"message": "Unauthorized"})

    response = client.get('/Account/get_cash')

    assert response.status_code == 401
    data = response.get_json()
    assert 'Unauthorized: Invalid API key' in data['message']


def test_get_cash_api_error(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = APIError({"message": "API error"}, 500)

    response = client.get('/Account/get_cash')

    assert response.status_code == 500
    data = response.get_json()
    assert 'Alpaca API error' in data['message']


def test_get_cash_unexpected_error(client, mock_alpaca_client):
    mock_alpaca_client.get_account.side_effect = Exception("Unexpected error")

    response = client.get('/Account/get_cash')

    assert response.status_code == 500
    data = response.get_json()
    assert 'An unexpected error occurred' in data['message']


def test_account_to_dict():
    mock_account = Mock()
    attributes = [
        'account_blocked', 'account_number', 'accrued_fees', 'balance_asof', 'bod_dtbp',
        'buying_power', 'cash', 'created_at', 'crypto_status', 'crypto_tier', 'currency',
        'daytrade_count', 'daytrading_buying_power', 'effective_buying_power', 'equity',
        'id', 'initial_margin', 'intraday_adjustments', 'last_equity', 'last_maintenance_margin',
        'long_market_value', 'maintenance_margin', 'multiplier', 'non_marginable_buying_power',
        'options_approved_level', 'options_buying_power', 'options_trading_level',
        'pattern_day_trader', 'pending_reg_taf_fees', 'portfolio_value', 'position_market_value',
        'regt_buying_power', 'short_market_value', 'shorting_enabled', 'sma', 'status',
        'trade_suspended_by_user', 'trading_blocked', 'transfers_blocked'
    ]

    for attr in attributes:
        setattr(mock_account, attr, f'value_{attr}')

    result = account_to_dict(mock_account)

    for attr in attributes:
        assert result[attr] == f'value_{attr}'


def test_account_to_dict_missing_attributes():
    mock_account = Mock(spec=[])
    mock_account.account_number = '123456789'
    mock_account.cash = '5000.00'

    result = account_to_dict(mock_account)

    assert result['account_number'] == '123456789'
    assert result['cash'] == '5000.00'
    assert result['equity'] is None  # This attribute wasn't set, so it should be None