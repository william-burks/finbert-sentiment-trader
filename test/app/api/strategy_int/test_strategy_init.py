import pytest
from unittest.mock import patch
from app.api.strategy_init import StrategyInit  # Adjust based on your structure
from config.config import BROKER, DEFAULT_SYMBOL, CASH_AT_RISK


@patch('app.api.strategy_init.MLTrader')  # Mock MLTrader at the correct import path
def test_strategy_init(mock_ml_trader):
    """Test initialization of StrategyInit."""

    # Initialize the strategy to trigger the MLTrader instantiation
    StrategyInit.initialize_strategy()

    # Check that MLTrader was called with the correct parameters
    mock_ml_trader.assert_called_once_with(
        name='api_strategy',
        broker=BROKER,
        parameters={"symbol": DEFAULT_SYMBOL, "cash_at_risk": CASH_AT_RISK}
    )

    # Ensure that StrategyInit.strategy is an instance of MLTrader
    assert isinstance(StrategyInit.strategy, mock_ml_trader.return_value.__class__)
