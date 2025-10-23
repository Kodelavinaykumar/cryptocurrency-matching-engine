"""
Order models and data structures for the matching engine.
"""

from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator
import uuid

class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    IOC = "ioc"  # Immediate-Or-Cancel
    FOK = "fok"  # Fill-Or-Kill

class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class Order(BaseModel):
    """Order model representing a trading order."""
    
    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    filled_quantity: Decimal = Field(default=Decimal('0'))
    remaining_quantity: Decimal = Field(default=Decimal('0'))
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v
    
    @validator('price')
    def validate_price(cls, v, values):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        if values.get('order_type') == OrderType.LIMIT and v is None:
            raise ValueError('Price is required for limit orders')
        return v
    
    @validator('remaining_quantity', always=True)
    def set_remaining_quantity(cls, v, values):
        if 'quantity' in values and 'filled_quantity' in values:
            return values['quantity'] - values['filled_quantity']
        return v
    
    def is_marketable(self, best_bid: Optional[Decimal], best_ask: Optional[Decimal]) -> bool:
        """Check if order is marketable (can be filled immediately)."""
        if self.order_type == OrderType.MARKET:
            return True
        
        if self.order_type in [OrderType.IOC, OrderType.FOK]:
            if self.price is None:
                return False
            if self.side == OrderSide.BUY and best_ask and self.price >= best_ask:
                return True
            if self.side == OrderSide.SELL and best_bid and self.price <= best_bid:
                return True
        
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': str(self.quantity),
            'price': str(self.price) if self.price else None,
            'filled_quantity': str(self.filled_quantity),
            'remaining_quantity': str(self.remaining_quantity),
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id
        }

class TradeExecution(BaseModel):
    """Trade execution model representing a completed trade."""
    
    trade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    price: Decimal
    quantity: Decimal
    aggressor_side: OrderSide
    maker_order_id: str
    taker_order_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    fee: Optional[Decimal] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade execution to dictionary."""
        return {
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'price': str(self.price),
            'quantity': str(self.quantity),
            'aggressor_side': self.aggressor_side.value,
            'maker_order_id': self.maker_order_id,
            'taker_order_id': self.taker_order_id,
            'timestamp': self.timestamp.isoformat(),
            'fee': str(self.fee) if self.fee else None
        }

class OrderBookLevel(BaseModel):
    """Order book level representing price and quantity at a specific price."""
    
    price: Decimal
    quantity: Decimal
    order_count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order book level to dictionary."""
        return {
            'price': str(self.price),
            'quantity': str(self.quantity),
            'order_count': self.order_count
        }

class BestBidOffer(BaseModel):
    """Best Bid and Offer (BBO) model."""
    
    symbol: str
    best_bid: Optional[OrderBookLevel] = None
    best_ask: Optional[OrderBookLevel] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert BBO to dictionary."""
        return {
            'symbol': self.symbol,
            'best_bid': self.best_bid.to_dict() if self.best_bid else None,
            'best_ask': self.best_ask.to_dict() if self.best_ask else None,
            'timestamp': self.timestamp.isoformat()
        }

class OrderBookSnapshot(BaseModel):
    """Complete order book snapshot."""
    
    symbol: str
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order book snapshot to dictionary."""
        return {
            'symbol': self.symbol,
            'bids': [level.to_dict() for level in self.bids],
            'asks': [level.to_dict() for level in self.asks],
            'timestamp': self.timestamp.isoformat()
        }
