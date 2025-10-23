"""
Performance benchmarks for the matching engine.
"""

import pytest
import asyncio
import time
from decimal import Decimal
from random import uniform, choice

from src.matching_engine.engine import MatchingEngine
from src.models.order import Order, OrderSide, OrderType

@pytest.fixture
async def matching_engine():
    """Create a matching engine instance for benchmarking."""
    engine = MatchingEngine()
    await engine.initialize()
    yield engine
    await engine.shutdown()

def generate_random_orders(count: int, symbol: str = "BTC-USDT") -> list[Order]:
    """Generate random orders for benchmarking."""
    orders = []
    
    for _ in range(count):
        side = choice([OrderSide.BUY, OrderSide.SELL])
        order_type = choice([OrderType.LIMIT, OrderType.MARKET, OrderType.IOC, OrderType.FOK])
        
        # Generate realistic price range
        price = Decimal(str(round(uniform(45000, 55000), 2)))
        quantity = Decimal(str(round(uniform(0.001, 10.0), 6)))
        
        order = Order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price if order_type == OrderType.LIMIT else None
        )
        orders.append(order)
    
    return orders

@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_order_submission_performance(matching_engine, benchmark):
    """Benchmark order submission performance."""
    orders = generate_random_orders(1000)
    
    async def submit_orders():
        results = []
        for order in orders:
            result = await matching_engine.submit_order(order)
            results.append(result)
        return results
    
    results = await benchmark(submit_orders)
    assert len(results) == 1000

@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_market_order_matching_performance(matching_engine, benchmark):
    """Benchmark market order matching performance."""
    # Pre-populate order book with limit orders
    limit_orders = []
    for i in range(100):
        order = Order(
            symbol="BTC-USDT",
            side=OrderSide.SELL if i % 2 == 0 else OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("1.0"),
            price=Decimal(str(50000 + i * 10))
        )
        limit_orders.append(order)
        await matching_engine.submit_order(order)
    
    # Generate market orders
    market_orders = []
    for _ in range(50):
        order = Order(
            symbol="BTC-USDT",
            side=choice([OrderSide.BUY, OrderSide.SELL]),
            order_type=OrderType.MARKET,
            quantity=Decimal("0.1")
        )
        market_orders.append(order)
    
    async def match_orders():
        results = []
        for order in market_orders:
            result = await matching_engine.submit_order(order)
            results.append(result)
        return results
    
    results = await benchmark(match_orders)
    assert len(results) == 50

@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_order_book_snapshot_performance(matching_engine, benchmark):
    """Benchmark order book snapshot generation performance."""
    # Pre-populate order book
    orders = generate_random_orders(500)
    for order in orders:
        await matching_engine.submit_order(order)
    
    def get_snapshots():
        snapshots = []
        for _ in range(100):
            snapshot = matching_engine.get_order_book_snapshot("BTC-USDT", depth=10)
            snapshots.append(snapshot)
        return snapshots
    
    snapshots = benchmark(get_snapshots)
    assert len(snapshots) == 100

@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_best_bid_offer_calculation_performance(matching_engine, benchmark):
    """Benchmark best bid and offer calculation performance."""
    # Pre-populate order book
    orders = generate_random_orders(200)
    for order in orders:
        await matching_engine.submit_order(order)
    
    def get_bbo():
        bbo_data = []
        for _ in range(1000):
            bbo = matching_engine.get_best_bid_offer("BTC-USDT")
            bbo_data.append(bbo)
        return bbo_data
    
    bbo_data = benchmark(get_bbo)
    assert len(bbo_data) == 1000

@pytest.mark.asyncio
async def test_throughput_measurement(matching_engine):
    """Measure orders per second throughput."""
    orders = generate_random_orders(1000)
    
    start_time = time.time()
    
    # Submit all orders
    for order in orders:
        await matching_engine.submit_order(order)
    
    end_time = time.time()
    duration = end_time - start_time
    orders_per_second = len(orders) / duration
    
    print(f"Processed {len(orders)} orders in {duration:.2f} seconds")
    print(f"Throughput: {orders_per_second:.2f} orders/second")
    
    # Assert minimum throughput requirement
    assert orders_per_second > 1000, f"Throughput {orders_per_second:.2f} orders/sec below minimum 1000"

@pytest.mark.asyncio
async def test_latency_measurement(matching_engine):
    """Measure order processing latency."""
    orders = generate_random_orders(100)
    latencies = []
    
    for order in orders:
        start_time = time.perf_counter()
        await matching_engine.submit_order(order)
        end_time = time.perf_counter()
        
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        latencies.append(latency)
    
    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    min_latency = min(latencies)
    
    print(f"Average latency: {avg_latency:.2f} ms")
    print(f"Max latency: {max_latency:.2f} ms")
    print(f"Min latency: {min_latency:.2f} ms")
    
    # Assert reasonable latency
    assert avg_latency < 10, f"Average latency {avg_latency:.2f}ms too high"
    assert max_latency < 50, f"Max latency {max_latency:.2f}ms too high"

@pytest.mark.asyncio
async def test_memory_usage(matching_engine):
    """Test memory usage with large number of orders."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Add many orders
    orders = generate_random_orders(10000)
    for order in orders:
        await matching_engine.submit_order(order)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    print(f"Initial memory: {initial_memory:.2f} MB")
    print(f"Final memory: {final_memory:.2f} MB")
    print(f"Memory increase: {memory_increase:.2f} MB")
    print(f"Memory per order: {memory_increase / len(orders) * 1024:.2f} KB")
    
    # Assert reasonable memory usage
    assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB too high"
    assert memory_increase / len(orders) * 1024 < 10, f"Memory per order {memory_increase / len(orders) * 1024:.2f}KB too high"
