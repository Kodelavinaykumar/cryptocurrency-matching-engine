"""
Test client for demonstrating the GoQuant Matching Engine functionality.
This client demonstrates order submission, market data streaming, and trade execution.
"""

import asyncio
import json
import websockets
import requests
from decimal import Decimal
from datetime import datetime
import random

class MatchingEngineClient:
    """Client for interacting with the GoQuant Matching Engine."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.ws_market_data = None
        self.ws_trades = None
    
    async def submit_order(self, symbol: str, side: str, order_type: str, quantity: str, price: str = None, user_id: str = None): # type: ignore
        """Submit an order to the matching engine."""
        url = f"{self.base_url}/api/v1/orders"
        data = {
            "symbol": symbol,
            "side": side,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "user_id": user_id
        }
        
        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}
        
        response = requests.post(url, params=data)
        return response.json()
    
    async def get_order(self, order_id: str):
        """Get order details by ID."""
        url = f"{self.base_url}/api/v1/orders/{order_id}"
        response = requests.get(url)
        return response.json()
    
    async def cancel_order(self, order_id: str):
        """Cancel an order."""
        url = f"{self.base_url}/api/v1/orders/{order_id}"
        response = requests.delete(url)
        return response.json()
    
    async def get_best_bid_offer(self, symbol: str):
        """Get current best bid and offer."""
        url = f"{self.base_url}/api/v1/market-data/{symbol}/bbo"
        response = requests.get(url)
        return response.json()
    
    async def get_order_book(self, symbol: str, depth: int = 10):
        """Get order book snapshot."""
        url = f"{self.base_url}/api/v1/market-data/{symbol}/orderbook"
        response = requests.get(url, params={"depth": depth})
        return response.json()
    
    async def connect_market_data(self, symbol: str):
        """Connect to market data WebSocket."""
        uri = f"ws://localhost:8000/api/v1/ws/market-data/{symbol}"
        self.ws_market_data = await websockets.connect(uri)
        return self.ws_market_data
    
    async def connect_trades(self, symbol: str):
        """Connect to trade execution WebSocket."""
        uri = f"ws://localhost:8000/api/v1/ws/trades/{symbol}"
        self.ws_trades = await websockets.connect(uri)
        return self.ws_trades
    
    async def listen_market_data(self, symbol: str):
        """Listen to market data updates."""
        if not self.ws_market_data:
            await self.connect_market_data(symbol)
        
        try:
            async for message in self.ws_market_data: # type: ignore
                data = json.loads(message)
                print(f"Market Data Update: {json.dumps(data, indent=2)}")
        except websockets.exceptions.ConnectionClosed:
            print("Market data connection closed")
    
    async def listen_trades(self, symbol: str):
        """Listen to trade executions."""
        if not self.ws_trades:
            await self.connect_trades(symbol)
        
        try:
            async for message in self.ws_trades: # type: ignore
                data = json.loads(message)
                print(f"Trade Execution: {json.dumps(data, indent=2)}")
        except websockets.exceptions.ConnectionClosed:
            print("Trade feed connection closed")

async def demonstrate_basic_functionality():
    """Demonstrate basic matching engine functionality."""
    print("=== GoQuant Matching Engine Demonstration ===\n")
    
    client = MatchingEngineClient()
    symbol = "BTC-USDT"
    
    # 1. Check system health
    print("1. Checking system health...")
    health_response = requests.get("http://localhost:8000/health")
    print(f"Health Status: {health_response.json()}\n")
    
    # 2. Submit some limit orders to build the order book
    print("2. Building order book with limit orders...")
    
    # Add some sell orders
    sell_orders = [
        ("BTC-USDT", "sell", "limit", "1.0", "51000.0"),
        ("BTC-USDT", "sell", "limit", "2.0", "52000.0"),
        ("BTC-USDT", "sell", "limit", "1.5", "53000.0"),
    ]
    
    for order_data in sell_orders:
        result = await client.submit_order(*order_data)
        print(f"Sell Order: {order_data} -> {result['status']}")
    
    # Add some buy orders
    buy_orders = [
        ("BTC-USDT", "buy", "limit", "1.0", "49000.0"),
        ("BTC-USDT", "buy", "limit", "2.0", "48000.0"),
        ("BTC-USDT", "buy", "limit", "1.5", "47000.0"),
    ]
    
    for order_data in buy_orders:
        result = await client.submit_order(*order_data)
        print(f"Buy Order: {order_data} -> {result['status']}")
    
    print()
    
    # 3. Display current order book
    print("3. Current order book:")
    order_book = await client.get_order_book(symbol, depth=5)
    print(json.dumps(order_book, indent=2))
    print()
    
    # 4. Display best bid and offer
    print("4. Best Bid and Offer:")
    bbo = await client.get_best_bid_offer(symbol)
    print(json.dumps(bbo, indent=2))
    print()
    
    # 5. Submit market orders to trigger matches
    print("5. Submitting market orders to trigger matches...")
    
    market_orders = [
        ("BTC-USDT", "buy", "market", "0.5"),
        ("BTC-USDT", "sell", "market", "0.3"),
    ]
    
    for order_data in market_orders:
        result = await client.submit_order(*order_data)
        print(f"Market Order: {order_data} -> {result['status']}")
        if result.get('fills'):
            print(f"  Fills: {result['fills']}")
    print()
    
    # 6. Test IOC order
    print("6. Testing IOC (Immediate-Or-Cancel) order...")
    ioc_result = await client.submit_order("BTC-USDT", "buy", "ioc", "1.0", "50000.0")
    print(f"IOC Order Result: {ioc_result}")
    print()
    
    # 7. Test FOK order
    print("7. Testing FOK (Fill-Or-Kill) order...")
    fok_result = await client.submit_order("BTC-USDT", "buy", "fok", "0.5", "51000.0")
    print(f"FOK Order Result: {fok_result}")
    print()
    
    # 8. Display updated order book
    print("8. Updated order book after matches:")
    order_book = await client.get_order_book(symbol, depth=5)
    print(json.dumps(order_book, indent=2))
    print()
    
    # 9. Test order cancellation
    print("9. Testing order cancellation...")
    # First, submit a limit order
    cancel_order_result = await client.submit_order("BTC-USDT", "buy", "limit", "1.0", "46000.0")
    if cancel_order_result.get('order_id'):
        order_id = cancel_order_result['order_id']
        print(f"Submitted order for cancellation: {order_id}")
        
        # Cancel the order
        cancel_result = await client.cancel_order(order_id)
        print(f"Cancellation result: {cancel_result}")
    print()

async def demonstrate_websocket_streaming():
    """Demonstrate real-time WebSocket streaming."""
    print("=== WebSocket Streaming Demonstration ===\n")
    
    client = MatchingEngineClient()
    symbol = "BTC-USDT"
    
    # Start WebSocket listeners in background
    market_data_task = asyncio.create_task(client.listen_market_data(symbol))
    trades_task = asyncio.create_task(client.listen_trades(symbol))
    
    # Give WebSocket connections time to establish
    await asyncio.sleep(1)
    
    print("WebSocket connections established. Submitting orders to trigger updates...\n")
    
    # Submit orders to trigger market data updates and trades
    orders = [
        ("BTC-USDT", "sell", "limit", "1.0", "54000.0"),
        ("BTC-USDT", "buy", "limit", "1.0", "46000.0"),
        ("BTC-USDT", "buy", "market", "0.5"),  # This should trigger a trade
        ("BTC-USDT", "sell", "market", "0.3"),  # This should trigger a trade
    ]
    
    for i, order_data in enumerate(orders):
        print(f"Submitting order {i+1}: {order_data}")
        result = await client.submit_order(*order_data)
        print(f"Result: {result['status']}")
        await asyncio.sleep(1)  # Wait between orders to see updates
    
    print("\nWebSocket demonstration complete. Connections will remain open for 10 seconds...")
    await asyncio.sleep(10)
    
    # Cancel background tasks
    market_data_task.cancel()
    trades_task.cancel()

async def demonstrate_performance():
    """Demonstrate system performance with bulk order submission."""
    print("=== Performance Demonstration ===\n")
    
    client = MatchingEngineClient()
    symbol = "BTC-USDT"
    
    # Generate random orders
    orders = []
    for i in range(100):
        side = random.choice(["buy", "sell"])
        order_type = random.choice(["limit", "market", "ioc", "fok"])
        quantity = str(round(random.uniform(0.1, 5.0), 3))
        price = str(round(random.uniform(45000, 55000), 2)) if order_type == "limit" else None
        
        orders.append((symbol, side, order_type, quantity, price))
    
    print(f"Submitting {len(orders)} orders for performance test...")
    
    start_time = asyncio.get_event_loop().time()
    
    # Submit all orders
    results = []
    for order_data in orders:
        result = await client.submit_order(*order_data)
        results.append(result)
    
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    
    # Calculate statistics
    successful_orders = sum(1 for r in results if r.get('status') in ['filled', 'partially_filled', 'pending'])
    filled_orders = sum(1 for r in results if r.get('status') == 'filled')
    pending_orders = sum(1 for r in results if r.get('status') == 'pending')
    
    print(f"Performance Results:")
    print(f"  Total orders: {len(orders)}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Orders per second: {len(orders) / duration:.2f}")
    print(f"  Successful orders: {successful_orders}")
    print(f"  Filled orders: {filled_orders}")
    print(f"  Pending orders: {pending_orders}")
    print()

async def main():
    """Main demonstration function."""
    print("Starting GoQuant Matching Engine Demonstration...\n")
    
    try:
        # Basic functionality demonstration
        await demonstrate_basic_functionality()
        
        # WebSocket streaming demonstration
        await demonstrate_websocket_streaming()
        
        # Performance demonstration
        await demonstrate_performance()
        
        print("Demonstration complete!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
