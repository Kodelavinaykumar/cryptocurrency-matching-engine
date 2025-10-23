"""
Unit tests for the matching engine core functionality.
"""

import pytest
import asyncio
from decimal import Decimal
from datetime import datetime

from src.matching_engine.engine import MatchingEngine
from src.models.order import Order, OrderSide, OrderType, OrderStatus

@pytest.fixture
async def matching_engine():
    """Create a matching engine instance for testing."""
    engine = MatchingEngine()
    await engine.initialize()
    yield engine
    await engine.shutdown()

@pytest.mark.asyncio
async def test_market_order_execution(matching_engine):
    """Test market order execution."""
    # Add a limit order to the book
    limit_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    result = await matching_engine.submit_order(limit_order)
    assert result["status"] == "pending"
    
    # Submit a market buy order
    market_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.5")
    )
    
    result = await matching_engine.submit_order(market_order)
    assert result["status"] == "filled"
    assert len(result["fills"]) == 1
    assert result["fills"][0]["price"] == "50000.0"
    assert result["fills"][0]["quantity"] == "0.5"

@pytest.mark.asyncio
async def test_limit_order_resting(matching_engine):
    """Test limit order resting on the book."""
    limit_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("49000.0")
    )
    
    result = await matching_engine.submit_order(limit_order)
    assert result["status"] == "pending"
    
    # Check that order is in the book
    order = matching_engine.get_order(limit_order.order_id)
    assert order is not None
    assert order.status == OrderStatus.PENDING

@pytest.mark.asyncio
async def test_price_time_priority(matching_engine):
    """Test price-time priority matching."""
    # Add first order
    order1 = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    result1 = await matching_engine.submit_order(order1)
    assert result1["status"] == "pending"
    
    # Add second order at same price
    order2 = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    result2 = await matching_engine.submit_order(order2)
    assert result2["status"] == "pending"
    
    # Submit market buy - should match first order (FIFO)
    market_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.5")
    )
    
    result = await matching_engine.submit_order(market_order)
    assert result["status"] == "filled"
    assert result["fills"][0]["maker_order_id"] == order1.order_id

@pytest.mark.asyncio
async def test_ioc_order_execution(matching_engine):
    """Test IOC order execution."""
    # Add limit order to book
    limit_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    await matching_engine.submit_order(limit_order)
    
    # Submit IOC order that can be filled
    ioc_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.IOC,
        quantity=Decimal("0.5"),
        price=Decimal("50000.0")
    )
    
    result = await matching_engine.submit_order(ioc_order)
    assert result["status"] == "filled"
    assert len(result["fills"]) == 1

@pytest.mark.asyncio
async def test_ioc_order_cancellation(matching_engine):
    """Test IOC order cancellation when not marketable."""
    # Submit IOC order that cannot be filled
    ioc_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.IOC,
        quantity=Decimal("1.0"),
        price=Decimal("49000.0")  # Lower than any sell orders
    )
    
    result = await matching_engine.submit_order(ioc_order)
    assert result["status"] == "cancelled"

@pytest.mark.asyncio
async def test_fok_order_execution(matching_engine):
    """Test FOK order execution."""
    # Add limit order to book
    limit_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    await matching_engine.submit_order(limit_order)
    
    # Submit FOK order that can be filled completely
    fok_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.FOK,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    result = await matching_engine.submit_order(fok_order)
    assert result["status"] == "filled"
    assert len(result["fills"]) == 1

@pytest.mark.asyncio
async def test_fok_order_cancellation(matching_engine):
    """Test FOK order cancellation when cannot be filled completely."""
    # Add limit order to book with insufficient quantity
    limit_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.5"),
        price=Decimal("50000.0")
    )
    
    await matching_engine.submit_order(limit_order)
    
    # Submit FOK order that requires more quantity than available
    fok_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.FOK,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    result = await matching_engine.submit_order(fok_order)
    assert result["status"] == "cancelled"

@pytest.mark.asyncio
async def test_order_cancellation(matching_engine):
    """Test order cancellation."""
    # Submit limit order
    limit_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("49000.0")
    )
    
    result = await matching_engine.submit_order(limit_order)
    assert result["status"] == "pending"
    
    # Cancel the order
    result = await matching_engine.cancel_order(limit_order.order_id)
    assert result["status"] == "cancelled"
    
    # Check order status
    order = matching_engine.get_order(limit_order.order_id)
    assert order.status == OrderStatus.CANCELLED

@pytest.mark.asyncio
async def test_best_bid_offer_calculation(matching_engine):
    """Test best bid and offer calculation."""
    # Add buy order
    buy_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("49000.0")
    )
    
    await matching_engine.submit_order(buy_order)
    
    # Add sell order
    sell_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    await matching_engine.submit_order(sell_order)
    
    # Check BBO
    bbo = matching_engine.get_best_bid_offer("BTC-USDT")
    assert bbo is not None
    assert bbo["best_bid"]["price"] == "49000.0"
    assert bbo["best_ask"]["price"] == "50000.0"

@pytest.mark.asyncio
async def test_order_book_snapshot(matching_engine):
    """Test order book snapshot generation."""
    # Add multiple orders
    orders = [
        Order(symbol="BTC-USDT", side=OrderSide.BUY, order_type=OrderType.LIMIT, quantity=Decimal("1.0"), price=Decimal("49000.0")),
        Order(symbol="BTC-USDT", side=OrderSide.BUY, order_type=OrderType.LIMIT, quantity=Decimal("2.0"), price=Decimal("48000.0")),
        Order(symbol="BTC-USDT", side=OrderSide.SELL, order_type=OrderType.LIMIT, quantity=Decimal("1.0"), price=Decimal("50000.0")),
        Order(symbol="BTC-USDT", side=OrderSide.SELL, order_type=OrderType.LIMIT, quantity=Decimal("2.0"), price=Decimal("51000.0")),
    ]
    
    for order in orders:
        await matching_engine.submit_order(order)
    
    # Get snapshot
    snapshot = matching_engine.get_order_book_snapshot("BTC-USDT", depth=2)
    assert snapshot is not None
    assert len(snapshot["bids"]) == 2
    assert len(snapshot["asks"]) == 2
    
    # Check ordering (bids descending, asks ascending)
    assert Decimal(snapshot["bids"][0]["price"]) > Decimal(snapshot["bids"][1]["price"])
    assert Decimal(snapshot["asks"][0]["price"]) < Decimal(snapshot["asks"][1]["price"])

@pytest.mark.asyncio
async def test_invalid_order_handling(matching_engine):
    """Test handling of invalid orders."""
    # Test negative quantity
    invalid_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("-1.0"),
        price=Decimal("50000.0")
    )
    
    result = await matching_engine.submit_order(invalid_order)
    assert result["status"] == "error"
    
    # Test unsupported symbol
    invalid_order = Order(
        symbol="INVALID-SYMBOL",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    result = await matching_engine.submit_order(invalid_order)
    assert result["status"] == "error"

@pytest.mark.asyncio
async def test_partial_fill_handling(matching_engine):
    """Test partial fill handling."""
    # Add sell order
    sell_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1.0"),
        price=Decimal("50000.0")
    )
    
    await matching_engine.submit_order(sell_order)
    
    # Submit buy order for more than available
    buy_order = Order(
        symbol="BTC-USDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("2.0")
    )
    
    result = await matching_engine.submit_order(buy_order)
    assert result["status"] == "partially_filled"
    assert result["filled_quantity"] == "1.0"
    assert result["remaining_quantity"] == "1.0"
