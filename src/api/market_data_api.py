"""
WebSocket API for real-time market data and trade execution feeds.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, HTTPException
from typing import Dict, Any, List
import json
import asyncio
import logging
from datetime import datetime

from src.models.order import TradeExecution
from src.matching_engine.engine import MatchingEngine

logger = logging.getLogger(__name__)

router = APIRouter()

def get_matching_engine(request: Request) -> MatchingEngine:
    """Get matching engine instance from app state."""
    return request.app.state.matching_engine

class ConnectionManager:
    """Manages WebSocket connections for market data and trade feeds."""
    
    def __init__(self):
        self.market_data_connections: Dict[str, List[WebSocket]] = {}
        self.trade_connections: Dict[str, List[WebSocket]] = {}
        self.active_connections: set = set()
    
    async def connect_market_data(self, websocket: WebSocket, symbol: str):
        """Connect WebSocket for market data feed."""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if symbol not in self.market_data_connections:
            self.market_data_connections[symbol] = []
        self.market_data_connections[symbol].append(websocket)
        
        logger.info(f"Market data connection established for {symbol}")
    
    async def connect_trades(self, websocket: WebSocket, symbol: str):
        """Connect WebSocket for trade execution feed."""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if symbol not in self.trade_connections:
            self.trade_connections[symbol] = []
        self.trade_connections[symbol].append(websocket)
        
        logger.info(f"Trade feed connection established for {symbol}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect WebSocket."""
        self.active_connections.discard(websocket)
        
        # Remove from market data connections
        for symbol, connections in self.market_data_connections.items():
            if websocket in connections:
                connections.remove(websocket)
        
        # Remove from trade connections
        for symbol, connections in self.trade_connections.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info("WebSocket connection closed")
    
    async def broadcast_market_data(self, symbol: str, data: Dict[str, Any]):
        """Broadcast market data to all connected clients for symbol."""
        if symbol in self.market_data_connections:
            message = json.dumps({
                "type": "market_data",
                "symbol": symbol,
                "data": data,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # Send to all connections for this symbol
            connections_to_remove = []
            for websocket in self.market_data_connections[symbol]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending market data: {e}")
                    connections_to_remove.append(websocket)
            
            # Remove failed connections
            for websocket in connections_to_remove:
                self.disconnect(websocket)
    
    async def broadcast_trade(self, symbol: str, trade: TradeExecution):
        """Broadcast trade execution to all connected clients for symbol."""
        if symbol in self.trade_connections:
            message = json.dumps({
                "type": "trade_execution",
                "symbol": symbol,
                "data": trade.to_dict(),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
            # Send to all connections for this symbol
            connections_to_remove = []
            for websocket in self.trade_connections[symbol]:
                try:
                    await websocket.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending trade data: {e}")
                    connections_to_remove.append(websocket)
            
            # Remove failed connections
            for websocket in connections_to_remove:
                self.disconnect(websocket)

# Global connection manager
connection_manager = ConnectionManager()

@router.websocket("/ws/market-data/{symbol}")
async def market_data_websocket(
    websocket: WebSocket,
    symbol: str,
    request: Request
):
    """
    WebSocket endpoint for real-time market data feed.
    
    Args:
        websocket: WebSocket connection
        symbol: Trading pair symbol
    """
    engine = get_matching_engine(request)
    
    # Validate symbol
    if symbol.upper() not in engine.get_supported_symbols():
        await websocket.close(code=1008, reason="Unsupported symbol")
        return
    
    await connection_manager.connect_market_data(websocket, symbol.upper())
    
    try:
        # Send initial order book snapshot
        snapshot = engine.get_order_book_snapshot(symbol.upper(), depth=10)
        if snapshot:
            await websocket.send_text(json.dumps({
                "type": "order_book_snapshot",
                "symbol": symbol.upper(),
                "data": snapshot,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }))
        
        # Keep connection alive
        while True:
            try:
                # Wait for ping from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "get_snapshot":
                    # Send current order book snapshot
                    snapshot = engine.get_order_book_snapshot(symbol.upper(), depth=10)
                    if snapshot:
                        await websocket.send_text(json.dumps({
                            "type": "order_book_snapshot",
                            "symbol": symbol.upper(),
                            "data": snapshot,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }))
                        
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text("ping")
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in market data WebSocket: {e}")
        connection_manager.disconnect(websocket)

@router.websocket("/ws/trades/{symbol}")
async def trades_websocket(
    websocket: WebSocket,
    symbol: str,
    request: Request
):
    """
    WebSocket endpoint for real-time trade execution feed.
    
    Args:
        websocket: WebSocket connection
        symbol: Trading pair symbol
    """
    engine = get_matching_engine(request)
    
    # Validate symbol
    if symbol.upper() not in engine.get_supported_symbols():
        await websocket.close(code=1008, reason="Unsupported symbol")
        return
    
    await connection_manager.connect_trades(websocket, symbol.upper())
    
    try:
        # Keep connection alive
        while True:
            try:
                # Wait for ping from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle ping/pong
                if data == "ping":
                    await websocket.send_text("pong")
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_text("ping")
                
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error in trades WebSocket: {e}")
        connection_manager.disconnect(websocket)

@router.get("/market-data/{symbol}/bbo")
async def get_best_bid_offer(
    symbol: str,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> Dict[str, Any]:
    """
    Get current best bid and offer for symbol.
    
    Args:
        symbol: Trading pair symbol
        
    Returns:
        Best bid and offer data
    """
    bbo = engine.get_best_bid_offer(symbol.upper())
    
    if not bbo:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    return bbo

@router.get("/market-data/{symbol}/orderbook")
async def get_order_book(
    symbol: str,
    depth: int = 10,
    engine: MatchingEngine = Depends(get_matching_engine)
) -> Dict[str, Any]:
    """
    Get order book snapshot for symbol.
    
    Args:
        symbol: Trading pair symbol
        depth: Number of levels to return (default: 10)
        
    Returns:
        Order book snapshot
    """
    snapshot = engine.get_order_book_snapshot(symbol.upper(), depth)
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="Symbol not found")
    
    return snapshot

@router.get("/market-data/symbols")
async def get_supported_symbols(
    engine: MatchingEngine = Depends(get_matching_engine)
) -> List[str]:
    """
    Get list of supported trading symbols.
    
    Returns:
        List of supported symbols
    """
    return engine.get_supported_symbols()

# Global functions for broadcasting (called by matching engine)
async def broadcast_market_data_update(symbol: str, data: Dict[str, Any]):
    """Broadcast market data update to all connected clients."""
    await connection_manager.broadcast_market_data(symbol, data)

async def broadcast_trade_execution(symbol: str, trade: TradeExecution):
    """Broadcast trade execution to all connected clients."""
    await connection_manager.broadcast_trade(symbol, trade)
