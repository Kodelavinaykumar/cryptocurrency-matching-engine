#!/usr/bin/env python3
"""
GoQuant Matching Engine - Main Application Entry Point
High-performance cryptocurrency matching engine with REG NMS compliance.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.matching_engine.engine import MatchingEngine
from src.api.order_api import router as order_router
from src.api.market_data_api import router as market_data_router, broadcast_market_data_update, broadcast_trade_execution

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('matching_engine.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Global matching engine instance
matching_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global matching_engine
    
    # Startup
    logger.info("Starting GoQuant Matching Engine...")
    matching_engine = MatchingEngine()
    
    # Add callbacks for real-time data streaming
    matching_engine.add_trade_callback(broadcast_trade_execution)
    matching_engine.add_market_data_callback(broadcast_market_data_update)
    
    logger.info("Matching engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down GoQuant Matching Engine...")
    if matching_engine:
        await matching_engine.shutdown()
    logger.info("Matching engine shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="GoQuant Matching Engine",
    description="High-performance cryptocurrency matching engine with REG NMS compliance",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(order_router, prefix="/api/v1", tags=["orders"])
app.include_router(market_data_router, prefix="/api/v1", tags=["market-data"])

@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "GoQuant Matching Engine",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global matching_engine
    
    if matching_engine is None:
        return {"status": "unhealthy", "message": "Matching engine not initialized"}
    
    try:
        # Get basic engine statistics
        stats = await matching_engine.get_statistics()
        return {
            "status": "healthy",
            "engine_status": "running",
            "supported_symbols": list(matching_engine.order_books.keys()),
            "active_orders": stats.get("total_orders", 0)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "message": str(e)}

# Make matching engine available to API endpoints
app.state.matching_engine = matching_engine

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
