import time

from flask import jsonify, Response, make_response
from flask_restx import Namespace, Resource, abort

from app.api.strategy_init import StrategyInit
api = Namespace('Strategy-Orders', description='Order operations')

@api.route('/create_order/<string:asset>/<int:quantity>/<string:side>')
@api.param('asset', 'The asset symbol (e.g., AAPL, GOOGL)')
@api.param('quantity', 'The quantity of the asset to purchase (e.g., 1, 2, ...n)')
@api.param('side', 'Order type (e.g., buy, sell)')
class CreateOrder(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('create_order')
    def post(self, asset, quantity, side):
        """Create a new stop limit order"""

        STOP_LOSS_MULTIPLIER = 0.95 if side == 'buy' else 1.05
        TAKE_PROFIT_MULTIPLIER = 1.20 if side == 'buy' else 0.80

        order = StrategyInit.initialize_strategy().strategy.create_order(
            asset,
            quantity,
            side.lower,
            StrategyInit.initialize_strategy().strategy.get_last_price(asset) * TAKE_PROFIT_MULTIPLIER, # Setting a take profit 20% above the purchase price
            StrategyInit.initialize_strategy().strategy.get_last_price(asset) * STOP_LOSS_MULTIPLIER, # Setting a stop loss 5% below the purchase price
        )
        return {'order': str(order)}

@api.route('/submit_order/<string:asset>/<int:quantity>/<string:side>')
@api.param('asset', 'The asset symbol (e.g., AAPL, GOOGL)')
@api.param('quantity', 'The quantity of the asset to purchase (e.g., 1, 2, ...n)')
@api.param('side', 'Order type (e.g., buy, sell)')
class SubmitOrder(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('submit_order')
    def post(self, asset, quantity, side):
        """Create, submit and open a new stop limit order"""
        order = StrategyInit.initialize_strategy().strategy.create_order(
            asset,
            quantity,
            side,
            round(StrategyInit.initialize_strategy().strategy.get_last_price(asset) * 1.20, 2), # Setting a take profit 20% above the purchase price
            round (StrategyInit.initialize_strategy().strategy.get_last_price(asset) * 0.95, 2), # Setting a stop loss 5% below the purchase price
        )
        StrategyInit.initialize_strategy().strategy.submit_order(order)
        # TODO: Replace with Async/Await
        time.sleep(0.25)
        new_order =  StrategyInit.initialize_strategy().strategy.get_order(order.identifier)
        return {'order': str(new_order)}

@api.route('/get_orders')
class GetOrders(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_orders')
    def get(self):
        """Get all current open orders"""
        orders = StrategyInit.initialize_strategy().strategy.get_orders()
        return {'orders': [str(order) for order in orders]}

@api.route('/sell_all/v2')
class SellAllV2(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('sell_allV2')
    def get(self):
        """Sell all strategy positions"""
        try:
            result = StrategyInit.initialize_strategy().strategy.sell_all()

            # Check if result is already a Response object
            if isinstance(result, Response):
                return result

            # If it's not a Response, create a JSON response
            response_data = {
                'status': 'success',
                'message': 'All positions sold successfully',
            }
            return make_response(jsonify(response_data), 200)
        except Exception as e:
            abort(500, message=f"An error occurred while selling all positions: {str(e)}")


def order_to_dict(order):
    return {
        'exchange': order.exchange,
        'type': order.type,
        'quantity': order.quantity,
        'asset': str(order.asset),
        'side': order.side,
        'limit_price': order.limit_price,
        'stop_price': order.stop_price,
        'status': "filled" if order.position_filled else "unfilled",
        'quote': order.quote,
    }

