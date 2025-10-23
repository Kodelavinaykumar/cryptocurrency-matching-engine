# GoQuant Matching Engine - System Architecture

## Overview

The GoQuant Matching Engine is a high-performance cryptocurrency trading system that implements REG NMS-inspired principles of price-time priority and internal order protection. The system is designed to process thousands of orders per second while maintaining strict compliance with financial market regulations.

## System Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer                                │
├─────────────────────┬───────────────────────────────────────┤
│   REST API          │           WebSocket APIs              │
│   - Order Submission│   - Market Data Streaming             │
│   - Order Management│   - Trade Execution Feed              │
│   - Market Data     │   - Real-time Updates                 │
└─────────────────────┴───────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Matching Engine Core                         │
├─────────────────────┬───────────────────────────────────────┤
│   Order Processing  │           Order Book                  │
│   - Validation      │   - Red-Black Tree Implementation     │
│   - Matching Logic  │   - Price-Time Priority               │
│   - Trade Generation│   - O(log n) Operations               │
└─────────────────────┴───────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Data Layer                                   │
├─────────────────────┬───────────────────────────────────────┤
│   Order Storage     │           Logging & Audit             │
│   - In-Memory Cache│   - Trade Execution Logs               │
│   - Order History   │   - System Diagnostics                │
│   - State Management│   - Performance Metrics               │
└─────────────────────┴───────────────────────────────────────┘
```

### Design Principles

1. **REG NMS Compliance**: Implements price-time priority matching with internal order protection
2. **High Performance**: Optimized for >1000 orders/second processing
3. **Low Latency**: Sub-millisecond order processing and matching
4. **Scalability**: Modular architecture supporting horizontal scaling
5. **Reliability**: Comprehensive error handling and logging
6. **Auditability**: Complete trade execution trail and audit logs

## Data Structures

### Order Book Implementation

The order book uses a **Red-Black Tree** data structure for optimal performance:

- **Time Complexity**: O(log n) for insert, delete, and search operations
- **Space Complexity**: O(n) for storing orders
- **Price-Time Priority**: FIFO ordering within each price level
- **Memory Efficiency**: Compact storage with minimal overhead

#### Red-Black Tree Properties

```python
class OrderBookNode:
    price: Decimal           # Price level
    orders: deque           # FIFO queue of orders at this price
    total_quantity: Decimal # Total quantity at this price level
    color: Color            # Red or Black for tree balancing
    left: OrderBookNode     # Left child
    right: OrderBookNode    # Right child
    parent: OrderBookNode   # Parent node
```

#### Order Book Operations

1. **Insertion**: O(log n) - Add new price level or order to existing level
2. **Deletion**: O(log n) - Remove order or entire price level
3. **Search**: O(log n) - Find specific price level
4. **Best Bid/Offer**: O(1) - Cached references to best levels
5. **Range Queries**: O(log n + k) - Get orders within price range

### Order Types and Processing

#### Market Orders
- Execute immediately at best available price
- No price limit, fills at current market price
- May result in partial fills if insufficient liquidity

#### Limit Orders
- Execute at specified price or better
- Rest on order book if not immediately marketable
- Support partial fills and order modification

#### IOC (Immediate-Or-Cancel)
- Execute immediately or cancel entirely
- No resting on order book
- Prevents trade-through violations

#### FOK (Fill-Or-Kill)
- Execute completely or cancel entirely
- All-or-nothing execution
- Ensures complete order fulfillment

## Matching Algorithm

### Price-Time Priority Implementation

The matching engine implements strict price-time priority:

1. **Price Priority**: Better prices execute first
   - Higher bids execute before lower bids
   - Lower asks execute before higher asks

2. **Time Priority**: FIFO within same price level
   - Earlier orders execute before later orders
   - Maintains fair and predictable execution

3. **Internal Order Protection**: No trade-throughs
   - Orders always execute at best available price
   - Prevents internal price improvement violations

### Matching Process Flow

```
Incoming Order
      │
      ▼
   Validate Order
      │
      ▼
   Check Marketability
      │
      ▼
   ┌─────────────────┐
   │ Marketable?     │
   └─────────────────┘
      │         │
      │ Yes     │ No
      ▼         ▼
   Match Orders  Add to Book
      │
      ▼
   Generate Trades
      │
      ▼
   Update Order Book
      │
      ▼
   Notify Subscribers
```

### Trade Execution Generation

Every matched order pair generates a trade execution record:

```python
class TradeExecution:
    trade_id: str           # Unique trade identifier
    symbol: str             # Trading pair
    price: Decimal          # Execution price
    quantity: Decimal       # Executed quantity
    aggressor_side: str     # Side of incoming order
    maker_order_id: str     # ID of resting order
    taker_order_id: str     # ID of incoming order
    timestamp: datetime     # Execution timestamp
    fee: Decimal           # Optional fee calculation
```

## API Design

### REST API Endpoints

#### Order Management
- `POST /api/v1/orders` - Submit new order
- `GET /api/v1/orders/{order_id}` - Get order details
- `DELETE /api/v1/orders/{order_id}` - Cancel order
- `GET /api/v1/orders` - List orders with filtering

#### Market Data
- `GET /api/v1/market-data/{symbol}/bbo` - Best bid and offer
- `GET /api/v1/market-data/{symbol}/orderbook` - Order book snapshot
- `GET /api/v1/market-data/symbols` - Supported symbols

### WebSocket APIs

#### Market Data Streaming
- `ws://localhost:8000/api/v1/ws/market-data/{symbol}`
- Real-time order book updates
- BBO changes and depth updates
- Heartbeat and ping/pong support

#### Trade Execution Feed
- `ws://localhost:8000/api/v1/ws/trades/{symbol}`
- Real-time trade executions
- Complete fill information
- Trade-by-trade audit trail

## Performance Characteristics

### Throughput
- **Target**: >1000 orders/second
- **Peak**: >10000 orders/second (with optimizations)
- **Sustained**: 5000+ orders/second

### Latency
- **Order Processing**: <1ms average
- **Matching**: <0.1ms average
- **WebSocket Updates**: <5ms end-to-end

### Memory Usage
- **Order Storage**: ~1KB per order
- **Order Book**: ~100KB per 1000 orders
- **Total System**: <100MB for 100K orders

## Error Handling and Logging

### Error Categories
1. **Validation Errors**: Invalid order parameters
2. **Business Logic Errors**: Insufficient liquidity, invalid symbols
3. **System Errors**: Internal failures, resource exhaustion
4. **Network Errors**: Connection failures, timeouts

### Logging Strategy
- **Structured Logging**: JSON format for easy parsing
- **Audit Trail**: Complete order and trade history
- **Performance Metrics**: Latency and throughput monitoring
- **Error Tracking**: Detailed error context and stack traces

### Log Levels
- **DEBUG**: Detailed execution flow
- **INFO**: Order submissions, trades, system events
- **WARNING**: Recoverable errors, performance issues
- **ERROR**: System errors, validation failures
- **CRITICAL**: System failures, data corruption

## Security Considerations

### Input Validation
- Strict parameter validation for all inputs
- Decimal precision handling for prices and quantities
- Symbol validation against supported pairs
- Order size limits and rate limiting

### Data Integrity
- Immutable order and trade records
- Cryptographic trade IDs
- Audit trail preservation
- State consistency checks

### Access Control
- API key authentication (future enhancement)
- Rate limiting per client
- Request validation and sanitization
- CORS configuration for web clients

## Scalability and Extensibility

### Horizontal Scaling
- Stateless API design
- Shared order book state (Redis)
- Load balancer distribution
- Microservice architecture

### Performance Optimizations
- Connection pooling
- Asynchronous processing
- Memory-mapped files
- CPU affinity binding

### Future Enhancements
- Advanced order types (Stop-Loss, Take-Profit)
- Fee calculation and management
- Order book persistence
- Multi-asset support
- Risk management integration

## Monitoring and Observability

### Key Metrics
- Orders per second
- Average processing latency
- Order book depth and spread
- Trade execution volume
- Error rates and types

### Health Checks
- System status endpoint
- Order book integrity checks
- Memory and CPU usage
- WebSocket connection health

### Alerting
- Performance degradation
- Error rate thresholds
- Resource exhaustion
- System failures

This architecture provides a robust, high-performance foundation for cryptocurrency trading while maintaining strict compliance with financial market regulations and best practices.
