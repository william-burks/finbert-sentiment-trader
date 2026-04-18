from flask_restx import Namespace, Resource, abort
from app.api.strategy_init import StrategyInit

api = Namespace('Strategy', description='Strategy operations')

# Initialize strategy once and reuse it
strategy_instance = StrategyInit.initialize_strategy()

@api.route('/get_cash')
class GetCash(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_cash')
    def get(self):
        """Get available cash in the account"""
        try:
            cash = strategy_instance.get_cash()
            return {'cash': cash}, 200
        except Exception as e:
            abort(500, message=f"Error retrieving cash: {str(e)}")

@api.route('/get_portfolio_value')
class GetPortfolioValue(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_portfolio_value')
    def get(self):
        """Get the current portfolio value"""
        try:
            portfolio_value = strategy_instance.get_portfolio_value()
            return {'portfolio_value': portfolio_value}, 200
        except Exception as e:
            abort(500, message=f"Error retrieving portfolio value: {str(e)}")

@api.route('/get_positions')
class GetPositions(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_positions')
    def get(self):
        """Get all current positions"""
        try:
            positions = strategy_instance.get_positions()
            return {'positions': [str(position) for position in positions]}, 200
        except Exception as e:
            abort(500, message=f"Error retrieving positions: {str(e)}")

@api.route('/get_last_price/<string:asset>')
@api.param('asset', 'The asset symbol (e.g., AAPL, GOOGL)')
class GetLastPrice(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_last_price')
    def get(self, asset):
        """Get the last price of an asset"""
        if not asset.isalpha():
            abort(400, message="Invalid asset symbol. Please use only alphabetic characters.")

        try:
            last_price = strategy_instance.get_last_price(asset)
            return {'last_price': last_price}, 200
        except Exception as e:
            abort(500, message=f"Error retrieving last price for {asset}: {str(e)}")

@api.route('/get_datetime')
class GetDatetime(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_datetime')
    def get(self):
        """Get the current datetime"""
        try:
            current_datetime = strategy_instance.get_datetime().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            return {'datetime': current_datetime}, 200
        except Exception as e:
            abort(500, message=f"Error retrieving datetime: {str(e)}")
