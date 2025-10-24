# GoQuant Matching Engine - API Specification

## Overview

This document provides a comprehensive specification of the GoQuant Matching Engine API, including REST endpoints and WebSocket connections for real-time data streaming.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.giquant.com`

## Authentication

Currently, the API does not require authentication for development purposes. In production, JWT tokens or API keys will be required.

## REST API Endpoints

### Health Check

#### GET /health

Check the health status of the matching engine.

**Response:**
```json
{
  "status": "healthy",
  "engine_status": "running",
  "supported_symbols": ["BTC-USDT", "ETH-USDT", "BNB-USDT"],
  "active_orders": 1234
}
```

**Status Codes:**
- `200 OK`: System is healthy
- `503 Service Unavailable`: System is unhealthy

### Order Management

#### POST /api/v1/orders

Submit a new order to the matching engine.

**Query Parameters:**
- `symbol` (string, required): Trading pair symbol (e.g., "BTC-USDT")
- `side` (string, required): Order side - "buy" or "sell"
- `order_type` (string, required): Order type - "market", "limit", "ioc", "fok"
- `quantity` (string, required): Order quantity (decimal string)
- `price` (string, optional): Order price (required for limit, ioc, fok orders)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/orders?symbol=BTC-USDT&side=buy&order_type=limit&quantity=1.5&price=50000.0"
```

**Response:**
```json
{
  "status": "pending",
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "symbol": "BTC-USDT",
  "side": "buy",
  "order_type": "limit",
  "quantity": "1.5",
  "price": "50000.0",
  "timestamp": "2023-10-22T15:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Order submitted successfully
- `400 Bad Request`: Invalid parameters
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

#### GET /api/v1/orders/{order_id}

Get the status of a specific order.

**Path Parameters:**
- `order_id` (string, required): Order identifier

**Response:**
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "symbol": "BTC-USDT",
  "side": "buy",
  "order_type": "limit",
  "quantity": "1.5",
  "price": "50000.0",
  "filled_quantity": "0.5",
  "remaining_quantity": "1.0",
  "status": "partially_filled",
  "timestamp": "2023-10-22T15:30:00Z",
  "fills": [
    {
      "trade_id": "456e7890-e89b-12d3-a456-426614174001",
      "price": "50000.0",
      "quantity": "0.5",
      "timestamp": "2023-10-22T15:30:05Z"
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Order found
- `404 Not Found`: Order not found
- `500 Internal Server Error`: Server error

#### DELETE /api/v1/orders/{order_id}

Cancel a specific order.

**Path Parameters:**
- `order_id` (string, required): Order identifier

**Response:**
```json
{
  "status": "cancelled",
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Order cancelled successfully"
}
```

**Status Codes:**
- `200 OK`: Order cancelled successfully
- `404 Not Found`: Order not found
- `400 Bad Request`: Order cannot be cancelled
- `500 Internal Server Error`: Server error

### Market Data

#### GET /api/v1/orderbook/{symbol}

Get the current order book for a trading pair.

**Path Parameters:**
- `symbol` (string, required): Trading pair symbol

**Query Parameters:**
- `depth` (integer, optional): Number of price levels to return (default: 10, max: 100)

**Response:**
```json
{
  "symbol": "BTC-USDT",
  "bids": [
    {
      "price": "50000.0",
      "quantity": "1.5",
      "order_count": 3
    },
    {
      "price": "49999.0",
      "quantity": "2.0",
      "order_count": 1
    }
  ],
  "asks": [
    {
      "price": "50001.0",
      "quantity": "1.0",
      "order_count": 2
    },
    {
      "price": "50002.0",
      "quantity": "0.5",
      "order_count": 1
    }
  ],
  "timestamp": "2023-10-22T15:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Order book retrieved successfully
- `404 Not Found`: Symbol not found
- `500 Internal Server Error`: Server error

#### GET /api/v1/bbo/{symbol}

Get the best bid and offer (BBO) for a trading pair.

**Path Parameters:**
- `symbol` (string, required): Trading pair symbol

**Response:**
```json
{
  "symbol": "BTC-USDT",
  "best_bid": {
    "price": "50000.0",
    "quantity": "1.5",
    "order_count": 3
  },
  "best_ask": {
    "price": "50001.0",
    "quantity": "1.0",
    "order_count": 2
  },
  "timestamp": "2023-10-22T15:30:00Z"
}
```

**Status Codes:**
- `200 OK`: BBO retrieved successfully
- `404 Not Found`: Symbol not found
- `500 Internal Server Error`: Server error

#### GET /api/v1/trades/{symbol}

Get recent trades for a trading pair.

**Path Parameters:**
- `symbol` (string, required): Trading pair symbol

**Query Parameters:**
- `limit` (integer, optional): Number of trades to return (default: 100, max: 1000)
- `since` (string, optional): ISO timestamp to get trades since

**Response:**
```json
{
  "symbol": "BTC-USDT",
  "trades": [
    {
      "trade_id": "456e7890-e89b-12d3-a456-426614174001",
      "price": "50000.0",
      "quantity": "0.5",
      "aggressor_side": "buy",
      "maker_order_id": "123e4567-e89b-12d3-a456-426614174000",
      "taker_order_id": "789e0123-e89b-12d3-a456-426614174002",
      "timestamp": "2023-10-22T15:30:05Z"
    }
  ],
  "timestamp": "2023-10-22T15:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Trades retrieved successfully
- `404 Not Found`: Symbol not found
- `500 Internal Server Error`: Server error

### Statistics

#### GET /api/v1/statistics

Get system statistics and performance metrics.

**Response:**
```json
{
  "total_orders": 1234,
  "total_trades": 567,
  "total_volume": "12345.67",
  "orders_per_second": 150.5,
  "average_latency_ms": 0.8,
  "active_symbols": 10,
  "timestamp": "2023-10-22T15:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Statistics retrieved successfully
- `500 Internal Server Error`: Server error

## WebSocket API

### Connection

Connect to WebSocket endpoints using the following URLs:

- **Market Data**: `ws://localhost:8000/ws/market-data/{symbol}`
- **Trades**: `ws://localhost:8000/ws/trades/{symbol}`

### Market Data Stream

#### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market-data/BTC-USDT');
```

#### Messages

**Order Book Updates:**
```json
{
  "type": "orderbook_update",
  "symbol": "BTC-USDT",
  "bids": [
    {
      "price": "50000.0",
      "quantity": "1.5",
      "order_count": 3
    }
  ],
  "asks": [
    {
      "price": "50001.0",
      "quantity": "1.0",
      "order_count": 2
    }
  ],
  "timestamp": "2023-10-22T15:30:00Z"
}
```

**Best Bid/Offer Updates:**
```json
{
  "type": "bbo_update",
  "symbol": "BTC-USDT",
  "best_bid": {
    "price": "50000.0",
    "quantity": "1.5",
    "order_count": 3
  },
  "best_ask": {
    "price": "50001.0",
    "quantity": "1.0",
    "order_count": 2
  },
  "timestamp": "2023-10-22T15:30:00Z"
}
```

### Trade Stream

#### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/trades/BTC-USDT');
```

#### Messages

**Trade Executions:**
```json
{
  "type": "trade_execution",
  "trade_id": "456e7890-e89b-12d3-a456-426614174001",
  "symbol": "BTC-USDT",
  "price": "50000.0",
  "quantity": "0.5",
  "aggressor_side": "buy",
  "maker_order_id": "123e4567-e89b-12d3-a456-426614174000",
  "taker_order_id": "789e0123-e89b-12d3-a456-426614174002",
  "timestamp": "2023-10-22T15:30:05Z"
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid order parameters",
    "details": {
      "field": "price",
      "reason": "Price is required for limit orders"
    }
  },
  "timestamp": "2023-10-22T15:30:00Z"
}
```

### Error Codes

- `VALIDATION_ERROR`: Invalid request parameters
- `ORDER_NOT_FOUND`: Order does not exist
- `INSUFFICIENT_LIQUIDITY`: Not enough liquidity for order
- `INVALID_SYMBOL`: Trading pair not supported
- `ORDER_CANNOT_BE_CANCELLED`: Order is in a state that cannot be cancelled
- `INTERNAL_ERROR`: Internal server error

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Rate Limiting

### Limits

- **REST API**: 1000 requests per minute per IP
- **WebSocket**: 100 connections per IP
- **Order Submission**: 100 orders per minute per user

### Headers

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Data Types

### Decimal Precision

All monetary values use decimal precision:
- **Price**: 8 decimal places
- **Quantity**: 8 decimal places
- **Volume**: 8 decimal places

### Timestamps

All timestamps are in ISO 8601 format with UTC timezone:
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Example: `2023-10-22T15:30:00Z`

### Order Status

- `pending`: Order is in the order book
- `partially_filled`: Order has been partially executed
- `filled`: Order has been completely executed
- `cancelled`: Order has been cancelled
- `rejected`: Order was rejected due to validation error

### Order Types

- `market`: Execute immediately at best available price
- `limit`: Execute only at specified price or better
- `ioc`: Immediate-Or-Cancel (execute immediately or cancel)
- `fok`: Fill-Or-Kill (execute completely or cancel entirely)

## Examples

### Python Client Example

```python
import requests
import websocket
import json

# Submit a limit order
response = requests.post(
    "http://localhost:8000/api/v1/orders",
    params={
        "symbol": "BTC-USDT",
        "side": "buy",
        "order_type": "limit",
        "quantity": "1.5",
        "price": "50000.0"
    }
)
order = response.json()
print(f"Order submitted: {order['order_id']}")

# Connect to WebSocket for real-time updates
def on_message(ws, message):
    data = json.loads(message)
    print(f"Received: {data}")

ws = websocket.WebSocketApp(
    "ws://localhost:8000/ws/market-data/BTC-USDT",
    on_message=on_message
)
ws.run_forever()
```

### JavaScript Client Example

```javascript
// Submit a limit order
fetch('/api/v1/orders?symbol=BTC-USDT&side=buy&order_type=limit&quantity=1.5&price=50000.0', {
    method: 'POST'
})
.then(response => response.json())
.then(order => {
    console.log('Order submitted:', order.order_id);
});

// Connect to WebSocket for real-time updates
const ws = new WebSocket('ws://localhost:8000/ws/market-data/BTC-USDT');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

## SDKs and Libraries

### Python

```bash
pip install giquant-client
```

```python
from giquant import MatchingEngineClient

client = MatchingEngineClient('http://localhost:8000')

# Submit order
order = client.submit_order(
    symbol='BTC-USDT',
    side='buy',
    order_type='limit',
    quantity=1.5,
    price=50000.0
)

# Get order status
status = client.get_order(order.order_id)

# Stream market data
for update in client.stream_market_data('BTC-USDT'):
    print(update)
```

### JavaScript/Node.js

```bash
npm install giquant-client
```

```javascript
const { MatchingEngineClient } = require('giquant-client');

const client = new MatchingEngineClient('http://localhost:8000');

// Submit order
const order = await client.submitOrder({
    symbol: 'BTC-USDT',
    side: 'buy',
    orderType: 'limit',
    quantity: 1.5,
    price: 50000.0
});

// Get order status
const status = await client.getOrder(order.orderId);

// Stream market data
client.streamMarketData('BTC-USDT', (update) => {
    console.log(update);
});
```

## Testing

### API Testing

Use the provided test client to verify API functionality:

```bash
python test_client.py
```

### WebSocket Testing

Test WebSocket connections using the browser console or a WebSocket testing tool:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/market-data/BTC-USDT');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log(JSON.parse(event.data));
ws.onerror = (error) => console.error('Error:', error);
```

## Support

For API support and questions:

1. Check the API documentation at `/docs` (Swagger UI)
2. Review the test client implementation
3. Check the server logs for detailed error information
4. Verify your request format against the examples

## Changelog

### Version 1.0.0
- Initial API release
- Support for Market, Limit, IOC, and FOK orders
- Real-time WebSocket streaming
- Comprehensive error handling
- Rate limiting and security features
