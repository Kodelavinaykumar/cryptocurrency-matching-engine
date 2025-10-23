# GoQuant Matching Engine - API Specification

## Overview

This document provides comprehensive API specifications for the GoQuant Matching Engine, including REST endpoints and WebSocket connections for real-time data streaming.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.goquant.io` (example)

## Authentication

Currently, the API does not require authentication. Future versions will support API key authentication.

## REST API

### Order Management

#### Submit Order

Submit a new order to the matching engine.

**Endpoint**: `POST /api/v1/orders`

**Parameters**:
- `symbol` (string, required): Trading pair symbol (e.g., "BTC-USDT")
- `side` (string, required): Order side ("buy" or "sell")
- `order_type` (string, required): Order type ("market", "limit", "ioc", "fok")
- `quantity` (string, required): Order quantity (decimal string)
- `price` (string, optional): Order price (required for limit orders)
- `user_id` (string, optional): User identifier

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -d "symbol=BTC-USDT&side=buy&order_type=limit&quantity=1.0&price=50000.0&user_id=user123"
```

**Example Response**:
```json
{
  "status": "pending",
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "filled_quantity": "0.0",
  "remaining_quantity": "1.0"
}
```

**Response Codes**:
- `200`: Order submitted successfully
- `400`: Invalid parameters
- `500`: Internal server error

#### Get Order

Retrieve order details by ID.

**Endpoint**: `GET /api/v1/orders/{order_id}`

**Parameters**:
- `order_id` (string, required): Order identifier

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/orders/123e4567-e89b-12d3-a456-426614174000"
```

**Example Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "symbol": "BTC-USDT",
  "side": "buy",
  "order_type": "limit",
  "quantity": "1.0",
  "price": "50000.0",
  "filled_quantity": "0.5",
  "remaining_quantity": "0.5",
  "status": "partially_filled",
  "timestamp": "2024-01-15T10:30:00.000000Z",
  "user_id": "user123"
}
```

#### Cancel Order

Cancel an active order.

**Endpoint**: `DELETE /api/v1/orders/{order_id}`

**Parameters**:
- `order_id` (string, required): Order identifier

**Example Request**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/orders/123e4567-e89b-12d3-a456-426614174000"
```

**Example Response**:
```json
{
  "status": "cancelled",
  "order_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### List Orders

Get list of orders with optional filtering.

**Endpoint**: `GET /api/v1/orders`

**Parameters**:
- `symbol` (string, optional): Filter by trading pair
- `user_id` (string, optional): Filter by user ID

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/orders?symbol=BTC-USDT&user_id=user123"
```

**Example Response**:
```json
[
  {
    "order_id": "123e4567-e89b-12d3-a456-426614174000",
    "symbol": "BTC-USDT",
    "side": "buy",
    "order_type": "limit",
    "quantity": "1.0",
    "price": "50000.0",
    "filled_quantity": "0.5",
    "remaining_quantity": "0.5",
    "status": "partially_filled",
    "timestamp": "2024-01-15T10:30:00.000000Z",
    "user_id": "user123"
  }
]
```

### Market Data

#### Get Best Bid and Offer

Get current best bid and offer for a symbol.

**Endpoint**: `GET /api/v1/market-data/{symbol}/bbo`

**Parameters**:
- `symbol` (string, required): Trading pair symbol

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/market-data/BTC-USDT/bbo"
```

**Example Response**:
```json
{
  "symbol": "BTC-USDT",
  "best_bid": {
    "price": "49950.0",
    "quantity": "2.5",
    "order_count": 3
  },
  "best_ask": {
    "price": "50050.0",
    "quantity": "1.8",
    "order_count": 2
  },
  "timestamp": "2024-01-15T10:30:00.000000Z"
}
```

#### Get Order Book Snapshot

Get order book snapshot with specified depth.

**Endpoint**: `GET /api/v1/market-data/{symbol}/orderbook`

**Parameters**:
- `symbol` (string, required): Trading pair symbol
- `depth` (integer, optional): Number of levels to return (default: 10)

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/market-data/BTC-USDT/orderbook?depth=5"
```

**Example Response**:
```json
{
  "symbol": "BTC-USDT",
  "bids": [
    {
      "price": "49950.0",
      "quantity": "2.5",
      "order_count": 3
    },
    {
      "price": "49900.0",
      "quantity": "1.2",
      "order_count": 1
    }
  ],
  "asks": [
    {
      "price": "50050.0",
      "quantity": "1.8",
      "order_count": 2
    },
    {
      "price": "50100.0",
      "quantity": "3.0",
      "order_count": 1
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000000Z"
}
```

#### Get Supported Symbols

Get list of supported trading symbols.

**Endpoint**: `GET /api/v1/market-data/symbols`

**Example Request**:
```bash
curl "http://localhost:8000/api/v1/market-data/symbols"
```

**Example Response**:
```json
[
  "BTC-USDT",
  "ETH-USDT",
  "BNB-USDT",
  "ADA-USDT",
  "SOL-USDT"
]
```

## WebSocket APIs

### Market Data Streaming

Real-time order book updates and market data changes.

**Endpoint**: `ws://localhost:8000/api/v1/ws/market-data/{symbol}`

**Parameters**:
- `symbol` (string, required): Trading pair symbol

**Connection Flow**:
1. Client connects to WebSocket
2. Server sends initial order book snapshot
3. Server sends real-time updates for order book changes
4. Client can send "ping" to keep connection alive
5. Client can send "get_snapshot" to request current snapshot

**Message Types**:

#### Order Book Snapshot
```json
{
  "type": "order_book_snapshot",
  "symbol": "BTC-USDT",
  "data": {
    "symbol": "BTC-USDT",
    "bids": [
      {
        "price": "49950.0",
        "quantity": "2.5",
        "order_count": 3
      }
    ],
    "asks": [
      {
        "price": "50050.0",
        "quantity": "1.8",
        "order_count": 2
      }
    ],
    "timestamp": "2024-01-15T10:30:00.000000Z"
  },
  "timestamp": "2024-01-15T10:30:00.000000Z"
}
```

#### Market Data Update
```json
{
  "type": "market_data",
  "symbol": "BTC-USDT",
  "data": {
    "symbol": "BTC-USDT",
    "best_bid": {
      "price": "49950.0",
      "quantity": "2.5",
      "order_count": 3
    },
    "best_ask": {
      "price": "50050.0",
      "quantity": "1.8",
      "order_count": 2
    },
    "timestamp": "2024-01-15T10:30:00.000000Z"
  },
  "timestamp": "2024-01-15T10:30:00.000000Z"
}
```

### Trade Execution Feed

Real-time trade execution notifications.

**Endpoint**: `ws://localhost:8000/api/v1/ws/trades/{symbol}`

**Parameters**:
- `symbol` (string, required): Trading pair symbol

**Message Types**:

#### Trade Execution
```json
{
  "type": "trade_execution",
  "symbol": "BTC-USDT",
  "data": {
    "trade_id": "trade-123e4567-e89b-12d3-a456-426614174000",
    "symbol": "BTC-USDT",
    "price": "50000.0",
    "quantity": "0.5",
    "aggressor_side": "buy",
    "maker_order_id": "maker-123e4567-e89b-12d3-a456-426614174000",
    "taker_order_id": "taker-123e4567-e89b-12d3-a456-426614174000",
    "timestamp": "2024-01-15T10:30:00.000000Z",
    "fee": "2.5"
  },
  "timestamp": "2024-01-15T10:30:00.000000Z"
}
```

## Error Handling

### Error Response Format

All API errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong",
  "status_code": 400,
  "error_type": "validation_error"
}
```

### Common Error Codes

- `400 Bad Request`: Invalid parameters or request format
- `404 Not Found`: Resource not found (order, symbol, etc.)
- `422 Unprocessable Entity`: Business logic validation failed
- `500 Internal Server Error`: Server-side error

### Error Examples

#### Invalid Order Parameters
```json
{
  "detail": "Quantity must be positive",
  "status_code": 400,
  "error_type": "validation_error"
}
```

#### Unsupported Symbol
```json
{
  "detail": "Unsupported symbol: INVALID-SYMBOL",
  "status_code": 400,
  "error_type": "validation_error"
}
```

#### Order Not Found
```json
{
  "detail": "Order not found",
  "status_code": 404,
  "error_type": "not_found"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Future versions will include:
- Per-client rate limiting
- Burst allowance
- Rate limit headers in responses

## WebSocket Connection Management

### Connection Lifecycle
1. Client establishes WebSocket connection
2. Server validates symbol and accepts connection
3. Server sends initial data snapshot
4. Server sends real-time updates
5. Client sends periodic ping messages
6. Connection closes on client disconnect or error

### Heartbeat Mechanism
- Client sends "ping" message every 30 seconds
- Server responds with "pong" message
- Server sends "ping" if no client message received for 30 seconds
- Connection closes if no response to ping

### Reconnection Strategy
- Client should implement exponential backoff for reconnections
- Reconnect on unexpected disconnection
- Handle connection errors gracefully
- Maintain order book state during reconnection

## Data Types and Precision

### Decimal Precision
- **Prices**: 8 decimal places maximum
- **Quantities**: 8 decimal places maximum
- **Fees**: 8 decimal places maximum

### Supported Symbols
Current supported trading pairs:
- BTC-USDT
- ETH-USDT
- BNB-USDT
- ADA-USDT
- SOL-USDT
- XRP-USDT
- DOT-USDT
- DOGE-USDT
- AVAX-USDT
- MATIC-USDT

### Order Types
- **market**: Execute immediately at best available price
- **limit**: Execute at specified price or better
- **ioc**: Immediate-Or-Cancel (execute immediately or cancel)
- **fok**: Fill-Or-Kill (execute completely or cancel)

### Order Sides
- **buy**: Buy order (bid)
- **sell**: Sell order (ask)

### Order Status
- **pending**: Order is active and waiting
- **partially_filled**: Order has been partially executed
- **filled**: Order has been completely executed
- **cancelled**: Order has been cancelled
- **rejected**: Order was rejected due to validation error

This API specification provides a complete reference for integrating with the GoQuant Matching Engine.
