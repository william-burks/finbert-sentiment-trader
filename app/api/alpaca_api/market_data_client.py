from collections import OrderedDict

import pytz

from app.api.alpaca_api.alpaca_client import AlpacaClient
from datetime import datetime, timedelta

from flask import jsonify
from flask_restx import Namespace, Resource
from alpaca_trade_api.rest import TimeFrame

api = Namespace('Market Data', description='Market Data related operations')


@api.route('/get_bars/<string:asset>/<string:timeframe>/<string:start>/<string:end>')
@api.param('timeframe', 'The timeframe (e.g., 1Min, 1H, 1D, 1W, 1M)')
@api.param('start', 'The start date (e.g., 2020-01-02)')
@api.param('end', 'The end date (e.g., 2020-01-02)')
@api.param('asset', 'The asset symbol (e.g., AAPL, GOOGL)')
class GetBars(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_bars')
    def get(self, asset, timeframe, start, end):
        '''Fetch Assets Bars'''
        try:
            alpaca_api = AlpacaClient().get_client()
            bars_df = alpaca_api.get_bars(asset, timeframe, start, end).df

            if 'timestamp' not in bars_df.columns:
                bars_df = bars_df.reset_index()

            bars_dict = bars_df.to_dict(orient='records')

            restructured_bars = []
            for bar in bars_dict:
                timestamp = bar.pop('timestamp')
                restructured_bars.append({
                    "timestamp": timestamp,
                    "bars": [bar]
                })

            response = {
                'asset': asset,
                'data': restructured_bars,
                'end': end,
                'start': start,
                'timeframe': timeframe
            }

            return jsonify(response)

        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/get_latest_bar/<string:asset>')
@api.param('asset', 'The asset symbol (e.g., AAPL, GOOGL)')
class GetLatestBar(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_latest_bar')
    def get(self, asset):
        '''Fetch Assets Latest Bar'''
        try:
            alpaca_api = AlpacaClient().get_client()
            bar = alpaca_api.get_latest_bar(asset)

            timestamp = bar.timestamp.isoformat()

            bar_data = {
                'close': bar.close,
                'high': bar.high,
                'low': bar.low,
                'trade count': bar.trade_count,
                'open': bar.open,
                'volume': bar.volume,
                'vwap': bar.vwap
            }

            result = {timestamp: bar_data}
            return jsonify(result)

        except Exception as e:
            return {'error': str(e)}, 500


@api.route('/get_asset/<string:symbol>')
@api.param('symbol', 'The asset symbol (e.g., AAPL, GOOGL)')
class GetAsset(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_asset')
    def get(self, symbol):
        '''Fetch Asset'''
        try:
            alpaca_api = AlpacaClient().get_client()
            asset = alpaca_api.get_asset(symbol)

            def get_value(obj, key, default='N/A'):
                if isinstance(obj, dict):
                    return obj.get(key, default)
                return getattr(obj, key, default)

            # Create a dictionary with all the attributes from the schema
            asset_dict = {
                'id': str(get_value(asset, 'id')),
                'class': str(get_value(asset, 'asset_class', get_value(asset, 'class'))),
                'exchange': str(get_value(asset, 'exchange')),
                'symbol': str(get_value(asset, 'symbol')),
                'name': str(get_value(asset, 'name')),
                'status': str(get_value(asset, 'status')),
                'tradable': bool(get_value(asset, 'tradable', False)),
                'marginable': bool(get_value(asset, 'marginable', False)),
                'shortable': bool(get_value(asset, 'shortable', False)),
                'easy_to_borrow': bool(get_value(asset, 'easy_to_borrow', False)),
                'fractionable': bool(get_value(asset, 'fractionable', False)),
                'attributes': list(get_value(asset, 'attributes', [])),
                'margin_requirement_long': str(get_value(asset, 'margin_requirement_long')),
                'margin_requirement_short': str(get_value(asset, 'margin_requirement_short')),
                'maintenance_margin_requirement': float(get_value(asset, 'maintenance_margin_requirement', 0))
            }

            return jsonify(asset_dict)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return {'error': str(e)}, 500