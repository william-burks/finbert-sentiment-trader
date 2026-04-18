from datetime import datetime
from flask import jsonify
from flask_restx import Namespace, Resource
from app.api.alpaca_api.alpaca_client import AlpacaClient

api = Namespace('News', description='News related operations')

@api.route('/get_news/<string:asset>/<string:start>/<string:end>')
@api.param('asset', 'The asset symbol (e.g., AAPL, GOOGL)')
@api.param('start', 'The start date (e.g., 2020-01-02)')
@api.param('end', 'The end date (e.g., 2020-01-02)')
class GetNews(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(500, 'Internal Server Error')
    @api.doc('get_news')
    def get(self, asset, start, end):
        '''Fetch News Details'''
        try:
            # Validate date format
            try:
                datetime.strptime(start, '%Y-%m-%d')
                datetime.strptime(end, '%Y-%m-%d')
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD.'}, 400

            alpaca_api = AlpacaClient().get_client()
            news = alpaca_api.get_news(symbol=asset, start=start, end=end)

            # Convert NewsV2 objects to dictionaries, excluding the 'images' field
            news_list = []
            for news_item in news:
                news_dict = {
                    'id': news_item.id,
                    'headline': news_item.headline,
                    'author': news_item.author,
                    'created_at': news_item.created_at.isoformat() if isinstance(news_item.created_at, datetime) else news_item.created_at,
                    'updated_at': news_item.updated_at.isoformat() if isinstance(news_item.updated_at, datetime) else news_item.updated_at,
                    'summary': news_item.summary,
                    'url': news_item.url,
                    'symbols': news_item.symbols,
                    'source': news_item.source
                }
                news_list.append(news_dict)

            return jsonify(news_list)
        except Exception as e:
            return {'message': f"An error occurred: {str(e)}"}, 500