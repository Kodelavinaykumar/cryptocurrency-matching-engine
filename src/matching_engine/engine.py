"""
Core matching engine implementing REG NMS principles.
Features price-time priority, internal order protection, and trade-through prevention.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Callable, Any
from decimal import Decimal
from datetime import datetime
import uuid

from src.models.order import Order, OrderSide, OrderType, OrderStatus, TradeExecution
from src.matching_engine.order_book import OrderBook
from src.config import settings

logger = logging.getLogger(__name__)

class MatchingEngine:
    """
    High-performance matching engine implementing REG NMS principles.
    
    Key Features:
    - Price-time priority matching
    - Internal order protection (no trade-throughs)
    - Support for Market, Limit, IOC, and FOK orders
    - Real-time trade execution generation
    - Comprehensive logging and audit trail
    """
    
    def __init__(self):
        self.order_books: Dict[str, OrderBook] = {}
        self.active_orders: Dict[str, Order] = {}
        self.trade_callbacks: List[Callable[[TradeExecution], None]] = []
        self.market_data_callbacks: List[Callable[[str, Any], None]] = []
        self.running = False
        self._lock = asyncio.Lock()
        
        # Initialize order books for supported symbols
        for symbol in settings.SUPPORTED_SYMBOLS:
            self.order_books[symbol] = OrderBook(symbol)
    
    async def initialize(self) -> None:
        """Initialize the matching engine."""
        logger.info("Initializing matching engine...")
        self.running = True
        logger.info(f"Initialized order books for {len(self.order_books)} symbols")
    
    async def shutdown(self) -> None:
        """Shutdown the matching engine."""
        logger.info("Shutting down matching engine...")
        self.running = False
        logger.info("Matching engine shutdown complete")
    
    def add_trade_callback(self, callback: Callable[[TradeExecution], None]) -> None:
        """Add callback for trade executions."""
        self.trade_callbacks.append(callback)
    
    def add_market_data_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Add callback for market data updates."""
        self.market_data_callbacks.append(callback)
    
    async def submit_order(self, order: Order) -> Dict[str, Any]:
        """
        Submit an order to the matching engine.
        
        Args:
            order: Order to submit
            
        Returns:
            Dictionary containing order status and any fills
        """
        async with self._lock:
            if not self.running:
                return {"status": "error", "message": "Matching engine not running"}
            
            if order.symbol not in self.order_books:
                return {"status": "error", "message": f"Unsupported symbol: {order.symbol}"}
            
            # Validate order
            validation_result = self._validate_order(order)
            if not validation_result["valid"]:
                return {"status": "error", "message": validation_result["message"]}
            
            # Store active order
            self.active_orders[order.order_id] = order
            
            # Process order based on type
            if order.order_type == OrderType.MARKET:
                return await self._process_market_order(order)
            elif order.order_type == OrderType.LIMIT:
                return await self._process_limit_order(order)
            elif order.order_type == OrderType.IOC:
                return await self._process_ioc_order(order)
            elif order.order_type == OrderType.FOK:
                return await self._process_fok_order(order)
            else:
                return {"status": "error", "message": f"Unsupported order type: {order.order_type}"}
    
    def _validate_order(self, order: Order) -> Dict[str, Any]:
        """Validate order parameters."""
        if order.quantity <= 0:
            return {"valid": False, "message": "Quantity must be positive"}
        
        if order.quantity < settings.MIN_ORDER_SIZE:
            return {"valid": False, "message": f"Quantity below minimum: {settings.MIN_ORDER_SIZE}"}
        
        if order.quantity > settings.MAX_ORDER_SIZE:
            return {"valid": False, "message": f"Quantity above maximum: {settings.MAX_ORDER_SIZE}"}
        
        if order.price is not None:
            if order.price <= 0:
                return {"valid": False, "message": "Price must be positive"}
            
            if order.price < settings.MIN_PRICE:
                return {"valid": False, "message": f"Price below minimum: {settings.MIN_PRICE}"}
            
            if order.price > settings.MAX_PRICE:
                return {"valid": False, "message": f"Price above maximum: {settings.MAX_PRICE}"}
        
        if order.order_type == OrderType.LIMIT and order.price is None:
            return {"valid": False, "message": "Price required for limit orders"}
        
        return {"valid": True}
    
    async def _process_market_order(self, order: Order) -> Dict[str, Any]:
        """Process market order - execute immediately at best available price."""
        order_book = self.order_books[order.symbol]
        bbo = order_book.get_best_bid_offer()
        
        if order.side == OrderSide.BUY:
            if not bbo.best_ask:
                return {"status": "error", "message": "No liquidity available for market buy"}
            max_price = bbo.best_ask.price
        else:
            if not bbo.best_bid:
                return {"status": "error", "message": "No liquidity available for market sell"}
            max_price = bbo.best_bid.price
        
        return await self._match_order(order, max_price)
    
    async def _process_limit_order(self, order: Order) -> Dict[str, Any]:
        """Process limit order - execute if marketable, otherwise add to book."""
        order_book = self.order_books[order.symbol]
        bbo = order_book.get_best_bid_offer()
        
        # Check if order is marketable
        if order.is_marketable(bbo.best_bid.price if bbo.best_bid else None,
                              bbo.best_ask.price if bbo.best_ask else None):
            # Execute immediately
            if order.side == OrderSide.BUY:
                max_price = order.price
            else:
                max_price = order.price
            
            result = await self._match_order(order, max_price)
            
            # If partially filled, add remainder to book
            if result["status"] == "partially_filled" and order.remaining_quantity > 0:
                order_book.add_order(order)
                await self._notify_market_data_update(order.symbol)
            
            return result
        else:
            # Add to order book
            order_book.add_order(order)
            await self._notify_market_data_update(order.symbol)
            return {"status": "pending", "order_id": order.order_id}
    
    async def _process_ioc_order(self, order: Order) -> Dict[str, Any]:
        """Process IOC order - execute immediately or cancel."""
        order_book = self.order_books[order.symbol]
        bbo = order_book.get_best_bid_offer()
        
        # IOC orders require a price
        if order.price is None:
            order.status = OrderStatus.REJECTED
            return {"status": "rejected", "order_id": order.order_id, "message": "IOC orders require a price"}
        
        if not order.is_marketable(bbo.best_bid.price if bbo.best_bid else None,
                                   bbo.best_ask.price if bbo.best_ask else None):
            # Cancel order
            order.status = OrderStatus.CANCELLED
            return {"status": "cancelled", "order_id": order.order_id}
        
        # Execute immediately
        if order.side == OrderSide.BUY:
            max_price = order.price
        else:
            max_price = order.price
        
        result = await self._match_order(order, max_price)
        
        # Cancel any remaining quantity
        if order.remaining_quantity > 0:
            order.status = OrderStatus.CANCELLED
        
        return result
    
    async def _process_fok_order(self, order: Order) -> Dict[str, Any]:
        """Process FOK order - execute completely or cancel entirely."""
        order_book = self.order_books[order.symbol]
        bbo = order_book.get_best_bid_offer()
        
        # FOK orders require a price
        if order.price is None:
            order.status = OrderStatus.REJECTED
            return {"status": "rejected", "order_id": order.order_id, "message": "FOK orders require a price"}
        
        if not order.is_marketable(bbo.best_bid.price if bbo.best_bid else None,
                                   bbo.best_ask.price if bbo.best_ask else None):
            # Cancel order
            order.status = OrderStatus.CANCELLED
            return {"status": "cancelled", "order_id": order.order_id}
        
        # Check if we can fill the entire order
        if order.side == OrderSide.BUY:
            max_price = order.price
        else:
            max_price = order.price
        
        # Get all marketable orders
        marketable_orders = order_book.get_marketable_orders(order.side, max_price)
        
        # Calculate total available quantity
        total_available = sum(o.remaining_quantity for o in marketable_orders)
        
        if total_available < order.quantity:
            # Cannot fill completely - cancel
            order.status = OrderStatus.CANCELLED
            return {"status": "cancelled", "order_id": order.order_id}
        
        # Execute completely
        result = await self._match_order(order, max_price)
        
        if order.remaining_quantity > 0:
            # This shouldn't happen for FOK, but handle it
            order.status = OrderStatus.CANCELLED
        
        return result
    
    async def _match_order(self, order: Order, max_price: Decimal) -> Dict[str, Any]:
        """
        Match order against the order book with price-time priority.
        
        Args:
            order: Order to match
            max_price: Maximum price to match at
            
        Returns:
            Dictionary containing match results
        """
        order_book = self.order_books[order.symbol]
        fills = []
        
        # Get marketable orders in price-time priority order
        marketable_orders = order_book.get_marketable_orders(order.side, max_price)
        
        for resting_order in marketable_orders:
            if order.remaining_quantity <= 0:
                break
            
            # Calculate fill quantity
            fill_quantity = min(order.remaining_quantity, resting_order.remaining_quantity)
            
            # Create trade execution
            trade = TradeExecution(
                symbol=order.symbol,
                price=resting_order.price,
                quantity=fill_quantity,
                aggressor_side=order.side,
                maker_order_id=resting_order.order_id,
                taker_order_id=order.order_id
            )
            
            # Update order quantities
            order.filled_quantity += fill_quantity
            order.remaining_quantity -= fill_quantity
            resting_order.filled_quantity += fill_quantity
            resting_order.remaining_quantity -= fill_quantity
            
            # Update order statuses
            if order.remaining_quantity <= 0:
                order.status = OrderStatus.FILLED
            elif order.filled_quantity > 0:
                order.status = OrderStatus.PARTIALLY_FILLED
            
            if resting_order.remaining_quantity <= 0:
                resting_order.status = OrderStatus.FILLED
                # Remove from order book
                order_book.remove_order(resting_order)
            elif resting_order.filled_quantity > 0:
                resting_order.status = OrderStatus.PARTIALLY_FILLED
            
            fills.append(trade)
            
            # Notify trade execution
            await self._notify_trade_execution(trade)
        
        # Update order book if needed
        if fills:
            await self._notify_market_data_update(order.symbol)
        
        # Determine final status
        if order.remaining_quantity <= 0:
            status = "filled"
        elif order.filled_quantity > 0:
            status = "partially_filled"
        else:
            status = "pending"
        
        return {
            "status": status,
            "order_id": order.order_id,
            "fills": [fill.to_dict() for fill in fills],
            "filled_quantity": str(order.filled_quantity),
            "remaining_quantity": str(order.remaining_quantity)
        }
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an active order."""
        async with self._lock:
            if order_id not in self.active_orders:
                return {"status": "error", "message": "Order not found"}
            
            order = self.active_orders[order_id]
            
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                return {"status": "error", "message": f"Order already {order.status.value}"}
            
            # Remove from order book if it's resting
            if order.order_type == OrderType.LIMIT and order.remaining_quantity > 0:
                order_book = self.order_books[order.symbol]
                order_book.remove_order(order)
                await self._notify_market_data_update(order.symbol)
            
            # Update order status
            order.status = OrderStatus.CANCELLED
            
            return {"status": "cancelled", "order_id": order_id}
    
    async def _notify_trade_execution(self, trade: TradeExecution) -> None:
        """Notify all trade execution callbacks."""
        for callback in self.trade_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(trade)
                else:
                    callback(trade)
            except Exception as e:
                logger.error(f"Error in trade callback: {e}")
    
    async def _notify_market_data_update(self, symbol: str) -> None:
        """Notify all market data callbacks."""
        order_book = self.order_books[symbol]
        bbo = order_book.get_best_bid_offer()
        
        for callback in self.market_data_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(symbol, bbo.to_dict())
                else:
                    callback(symbol, bbo.to_dict())
            except Exception as e:
                logger.error(f"Error in market data callback: {e}")
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self.active_orders.get(order_id)
    
    def get_best_bid_offer(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get best bid and offer for symbol."""
        if symbol not in self.order_books:
            return None
        
        return self.order_books[symbol].get_best_bid_offer().to_dict()
    
    def get_order_book_snapshot(self, symbol: str, depth: int = 10) -> Optional[Dict[str, Any]]:
        """Get order book snapshot for symbol."""
        if symbol not in self.order_books:
            return None
        
        return self.order_books[symbol].get_order_book_snapshot(depth).to_dict()
    
    def get_supported_symbols(self) -> List[str]:
        """Get list of supported trading symbols."""
        return list(self.order_books.keys())
    
    def get_total_active_orders(self) -> int:
        """Get total number of active orders."""
        return len(self.active_orders)
    
    def get_active_orders_for_symbol(self, symbol: str) -> List[Order]:
        """Get all active orders for a specific symbol."""
        return [order for order in self.active_orders.values() if order.symbol == symbol]
