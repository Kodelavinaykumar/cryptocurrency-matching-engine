# GoQuant Matching Engine - Architecture Guide

## Overview

The GoQuant Matching Engine is a high-performance cryptocurrency matching engine that implements REG NMS-inspired principles of price-time priority and internal order protection. This document provides a comprehensive overview of the system architecture, design decisions, and implementation details.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   REST API      │    │  WebSocket API  │    │   Client Apps   │
│   (FastAPI)     │    │   (FastAPI)     │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────────────┘
          │                      │
          └──────────┬───────────┘
                     │
          ┌─────────────────┐
          │  Matching Engine│
          │   (Core Logic)  │
          └─────────┬───────┘
                    │
          ┌─────────────────┐
          │   Order Books   │
          │ (Red-Black Tree)│
          └─────────────────┘
```

### Core Components

#### 1. Matching Engine (`src/matching_engine/engine.py`)

The heart of the system, responsible for:
- Order validation and preprocessing
- Price-time priority matching
- Trade execution generation
- Order book management
- Real-time event broadcasting

**Key Features:**
- Asynchronous processing for high throughput
- REG NMS compliance with price-time priority
- Support for Market, Limit, IOC, and FOK orders
- Comprehensive error handling and logging

#### 2. Order Book (`src/matching_engine/order_book.py`)

Implements a red-black tree data structure for efficient order management:

**Data Structure:**
```python
class OrderBook:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.bids = RedBlackTree()  # Buy orders (price descending)
        self.asks = RedBlackTree()  # Sell orders (price ascending)
        self.orders = {}            # Order lookup by ID
```

**Operations:**
- **Insert**: O(log n) - Add new orders
- **Delete**: O(log n) - Remove orders
- **Search**: O(log n) - Find orders by price
- **BBO**: O(1) - Get best bid/offer

#### 3. Order Models (`src/models/order.py`)

Defines the core data structures:

```python
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal]
    timestamp: datetime
    status: OrderStatus
```

**Order Types:**
- **Market**: Execute immediately at best available price
- **Limit**: Execute only at specified price or better
- **IOC**: Execute immediately or cancel (Immediate-Or-Cancel)
- **FOK**: Execute completely or cancel entirely (Fill-Or-Kill)

#### 4. API Layer

**REST API (`src/api/order_api.py`):**
- Order submission and management
- Order book queries
- Health checks and statistics

**WebSocket API (`src/api/market_data_api.py`):**
- Real-time market data streaming
- Trade execution feeds
- Order book updates

## Data Structures

### Red-Black Tree Implementation

The order book uses a red-black tree for efficient price-level management:

```python
class RedBlackTree:
    def __init__(self):
        self.root = None
        self.size = 0
    
    def insert(self, price: Decimal, order: Order):
        # O(log n) insertion with automatic balancing
        
    def delete(self, price: Decimal):
        # O(log n) deletion with automatic balancing
        
    def find(self, price: Decimal) -> Optional[OrderBookNode]:
        # O(log n) search
```

**Properties:**
- **Height**: O(log n) - Guaranteed balanced tree
- **Operations**: All operations are O(log n)
- **Memory**: O(n) - Linear space complexity
- **Balancing**: Automatic rebalancing after insertions/deletions

### FIFO Queues for Price Levels

Each price level maintains a FIFO queue for time priority:

```python
class PriceLevel:
    def __init__(self, price: Decimal):
        self.price = price
        self.orders = deque()  # FIFO queue
        self.total_quantity = Decimal('0')
        self.order_count = 0
```

**Benefits:**
- **Time Priority**: First-in, first-out within same price
- **Efficiency**: O(1) append/pop operations
- **Memory**: Efficient storage of multiple orders at same price

## Matching Algorithm

### Price-Time Priority

The matching algorithm implements strict REG NMS compliance:

```python
async def _match_order(self, order: Order, max_price: Decimal):
    """Match order using price-time priority."""
    order_book = self.order_books[order.symbol]
    
    # Get marketable orders (orders that can be matched)
    marketable_orders = order_book.get_marketable_orders(order.side, max_price)
    
    for resting_order in marketable_orders:
        if order.remaining_quantity <= 0:
            break
        
        # Calculate fill quantity
        fill_quantity = min(order.remaining_quantity, resting_order.remaining_quantity)
        
        # Create trade execution
        trade = TradeExecution(
            trade_id=str(uuid.uuid4()),
            symbol=order.symbol,
            price=resting_order.price,
            quantity=fill_quantity,
            aggressor_side=order.side,
            maker_order_id=resting_order.order_id,
            taker_order_id=order.order_id,
            timestamp=datetime.utcnow()
        )
        
        # Update quantities and statuses
        # Broadcast trade execution
        # Update order book
```

### Order Processing Flow

1. **Order Validation**: Check parameters and business rules
2. **Order Type Processing**: Handle different order types appropriately
3. **Matching**: Apply price-time priority algorithm
4. **Execution**: Generate trades and update order book
5. **Broadcasting**: Send real-time updates via WebSocket
6. **Logging**: Record all operations for audit trail

## Performance Optimizations

### Asynchronous Processing

The entire system is built on async/await for high concurrency:

```python
async def submit_order(self, order: Order) -> Dict[str, Any]:
    """Submit order asynchronously."""
    # Non-blocking order processing
    result = await self._process_order(order)
    return result
```

**Benefits:**
- **Concurrency**: Handle thousands of concurrent orders
- **Non-blocking**: I/O operations don't block processing
- **Scalability**: Efficient resource utilization

### Memory Management

- **Object Pooling**: Reuse frequently created objects
- **Efficient Data Structures**: Red-black tree for O(log n) operations
- **Garbage Collection**: Optimized for minimal GC pressure
- **Memory Profiling**: Continuous monitoring of memory usage

### Connection Management

- **WebSocket Pooling**: Efficient connection management
- **Message Batching**: Batch updates for better throughput
- **Compression**: Message compression for bandwidth optimization
- **Heartbeat**: Connection health monitoring

## Error Handling and Logging

### Comprehensive Error Handling

```python
try:
    result = await self._process_order(order)
except ValidationError as e:
    logger.error(f"Order validation failed: {e}")
    return {"status": "rejected", "error": str(e)}
except Exception as e:
    logger.error(f"Unexpected error processing order: {e}")
    return {"status": "error", "error": "Internal server error"}
```

### Structured Logging

```python
logger.info(
    "Order processed",
    extra={
        "order_id": order.order_id,
        "symbol": order.symbol,
        "side": order.side.value,
        "order_type": order.order_type.value,
        "quantity": str(order.quantity),
        "price": str(order.price) if order.price else None,
        "status": order.status.value
    }
)
```

## Security Considerations

### Input Validation

- **Pydantic Models**: Strict type checking and validation
- **Range Validation**: Price and quantity bounds checking
- **Format Validation**: Symbol format and order type validation
- **SQL Injection Prevention**: Parameterized queries

### Rate Limiting

- **API Rate Limiting**: Prevent abuse and ensure fair access
- **Order Rate Limiting**: Limit orders per user per second
- **Connection Limits**: Maximum concurrent connections

## Monitoring and Observability

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "engine_status": "running",
        "supported_symbols": list(matching_engine.order_books.keys()),
        "active_orders": stats.get("total_orders", 0)
    }
```

### Metrics Collection

- **Performance Metrics**: Orders per second, latency, throughput
- **System Metrics**: Memory usage, CPU utilization, connection count
- **Business Metrics**: Trade volume, order book depth, fill rates

### Logging Strategy

- **Structured Logging**: JSON format for easy parsing
- **Correlation IDs**: Track requests across services
- **Log Levels**: Appropriate logging levels for different scenarios
- **Log Rotation**: Automatic log file rotation and cleanup

## Scalability Considerations

### Horizontal Scaling

- **Stateless Design**: No shared state between instances
- **Load Balancing**: Ready for load balancer integration
- **Database Sharding**: Prepared for database scaling
- **Microservices**: Modular architecture for service splitting

### Vertical Scaling

- **Multi-threading**: Parallel order processing
- **CPU Optimization**: Efficient algorithm implementation
- **Memory Optimization**: Minimal memory footprint
- **I/O Optimization**: Async operations for better throughput

## Testing Strategy

### Unit Testing

- **Core Logic**: Comprehensive testing of matching algorithms
- **Data Structures**: Red-black tree and order book testing
- **API Endpoints**: REST and WebSocket API testing
- **Error Handling**: Edge case and error scenario testing

### Integration Testing

- **End-to-End**: Complete order processing flow
- **Performance**: Load and stress testing
- **WebSocket**: Real-time communication testing
- **Database**: Persistence layer testing

### Performance Testing

- **Benchmarks**: Automated performance benchmarks
- **Load Testing**: High-load scenario testing
- **Memory Testing**: Memory usage and leak testing
- **Latency Testing**: End-to-end latency measurement

## Deployment Architecture

### Development Environment

```bash
# Local development
python main.py

# With Docker
docker-compose up
```

### Production Environment

- **Kubernetes**: Container orchestration
- **Load Balancer**: Traffic distribution
- **Database**: PostgreSQL with Redis caching
- **Monitoring**: Prometheus and Grafana
- **Logging**: Centralized logging with ELK stack

## Future Enhancements

### Planned Features

1. **Advanced Order Types**: Stop orders, trailing stops
2. **Fee Calculation**: Maker/taker fee model
3. **Risk Management**: Position limits and risk controls
4. **Market Data**: Level 2 market data feeds
5. **Analytics**: Trading analytics and reporting

### Performance Improvements

1. **Multi-threading**: Parallel order processing
2. **Memory Pooling**: Object pool optimization
3. **Network Optimization**: Binary protocols
4. **Caching**: Intelligent caching strategies
5. **Compression**: Message compression

## Conclusion

The GoQuant Matching Engine represents a sophisticated implementation of a high-performance trading system. The architecture emphasizes:

- **Performance**: O(log n) operations with high throughput
- **Reliability**: Comprehensive error handling and logging
- **Scalability**: Horizontal and vertical scaling capabilities
- **Compliance**: REG NMS regulatory compliance
- **Maintainability**: Clean, well-documented code

The system is designed to handle the demands of high-frequency trading while maintaining strict regulatory compliance and operational excellence.
