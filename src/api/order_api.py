"""
REST API for order submission and management.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List
from decimal import Decimal
import logging

from src.models.order import Order, OrderSide, OrderType, OrderStatus
from src.matching_engine.engine import MatchingEngine

logger = logging.getLogger(__name__)

router = APIRouter()

def get_matching_engine(request: Request) -> MatchingEngine:
    """Get matching engine instance from app state."""
    return request.app.state.matching_engine

class OrderRequest:
    """Order submission request model."""
    def __init__(self, symbol: str, side: str, order_type: str, quantity: str, price: str = None, user_id: str = None):
        self.symbol = symbol
        self.side = side
        self.order_type = order_type
        self.quantity = Decimal(quantity)
        self.price = Decimal(price) if price else None
        self.user_id = user_id

@router.post("/orders")
async def submit_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str = None,
    user_id: str = None,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> Dict[str, Any]:
    """
    Submit a new order to the matching engine.
    
    Args:
        symbol: Trading pair symbol (e.g., "BTC-USDT")
        side: Order side ("buy" or "sell")
        order_type: Order type ("market", "limit", "ioc", "fok")
        quantity: Order quantity
        price: Order price (required for limit orders)
        user_id: Optional user identifier
        
    Returns:
        Order submission result with status and fills
    """
    try:
        # Validate inputs
        if side not in ["buy", "sell"]:
            raise HTTPException(status_code=400, detail="Invalid side. Must be 'buy' or 'sell'")
        
        if order_type not in ["market", "limit", "ioc", "fok"]:
            raise HTTPException(status_code=400, detail="Invalid order type. Must be 'market', 'limit', 'ioc', or 'fok'")
        
        # Create order
        order = Order(
            symbol=symbol.upper(),
            side=OrderSide(side),
            order_type=OrderType(order_type),
            quantity=Decimal(quantity),
            price=Decimal(price) if price else None,
            user_id=user_id
        )
        
        # Submit to matching engine
        result = await engine.submit_order(order)
        
        logger.info(f"Order submitted: {order.order_id} - {order.symbol} {order.side} {order.quantity} @ {order.price}")
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting order: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> Dict[str, Any]:
    """
    Get order details by ID.
    
    Args:
        order_id: Order identifier
        
    Returns:
        Order details
    """
    order = engine.get_order(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order.to_dict()

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> Dict[str, Any]:
    """
    Cancel an active order.
    
    Args:
        order_id: Order identifier
        
    Returns:
        Cancellation result
    """
    result = await engine.cancel_order(order_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    logger.info(f"Order cancelled: {order_id}")
    
    return result

@router.get("/orders")
async def get_orders(
    symbol: str = None,
    user_id: str = None,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> List[Dict[str, Any]]:
    """
    Get orders with optional filtering.
    
    Args:
        symbol: Filter by trading pair
        user_id: Filter by user ID
        
    Returns:
        List of orders
    """
    orders = []
    
    for order in engine.active_orders.values():
        if symbol and order.symbol != symbol.upper():
            continue
        if user_id and order.user_id != user_id:
            continue
        
        orders.append(order.to_dict())
    
    return orders

@router.get("/orders/symbol/{symbol}")
async def get_orders_for_symbol(
    symbol: str,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> List[Dict[str, Any]]:
    """
    Get all active orders for a specific symbol.
    
    Args:
        symbol: Trading pair symbol
        
    Returns:
        List of orders for the symbol
    """
    orders = engine.get_active_orders_for_symbol(symbol.upper())
    return [order.to_dict() for order in orders]
