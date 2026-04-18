from unittest.mock import Mock

from flask import jsonify, make_response
from flask_restx import Namespace, Resource
from app.api.alpaca_api.alpaca_client import AlpacaClient
from alpaca_trade_api.rest import APIError

api = Namespace('Account', description='Account related operations')

@api.route('/get_account')
class GetAccount(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(401, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_account')
    def get(self) -> object:
        '''Fetch Account Details'''
        try:
            alpaca_api = AlpacaClient().get_client()
            account = alpaca_api.get_account()
            account_dict = account_to_dict(account)
            return make_response(jsonify(account_dict), 200)
        except APIError as e:
            error_message = str(e)
            if 'unauthorized' in error_message.lower():
                return make_response({'message': 'Unauthorized: Invalid API key'}, 401)
            elif 'bad request' in error_message.lower():
                return make_response({'message': f'Bad request: {error_message}'}, 400)
            else:
                return make_response({'message': f'Alpaca API error: {error_message}'}, 500)
        except Exception as e:
            return make_response({'message': f'An unexpected error occurred: {str(e)}'}, 500)


@api.route('/get_cash')
class GetCash(Resource):
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_cash')
    def get(self):
        '''Fetch Account Cash'''
        try:
            alpaca_api = AlpacaClient().get_client()
            account = alpaca_api.get_account()
            return {'Cash': account.cash}, 200
        except APIError as e:
            error_message = str(e)
            if 'unauthorized' in error_message.lower():
                return {'message': 'Unauthorized: Invalid API key'}, 401
            else:
                return {'message': f'Alpaca API error: {error_message}'}, 500
        except Exception as e:
            return {'message': f'An unexpected error occurred: {str(e)}'}, 500


def account_to_dict(account):
    account_dict = {}
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
        value = getattr(account, attr, None)
        if isinstance(value, Mock):
            account_dict[attr] = str(value)
        else:
            account_dict[attr] = value

    return account_dict