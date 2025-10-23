"""
GoQuant Cryptocurrency Matching Engine
Main entry point for the matching engine application.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.api.order_api import router as order_router
from src.api.market_data_api import router as market_data_router, broadcast_market_data_update, broadcast_trade_execution
from src.matching_engine.engine import MatchingEngine
from src.config import settings

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
    """Application lifespan manager for startup and shutdown."""
    global matching_engine
    
    # Startup
    logger.info("Starting GoQuant Matching Engine...")
    matching_engine = MatchingEngine()
    await matching_engine.initialize()
    
    # Add callbacks for real-time data streaming
    matching_engine.add_trade_callback(lambda trade: asyncio.create_task(broadcast_trade_execution(trade.symbol, trade)))
    matching_engine.add_market_data_callback(lambda symbol, data: asyncio.create_task(broadcast_market_data_update(symbol, data)))
    
    # Store engine instance in app state for API access
    app.state.matching_engine = matching_engine
    
    logger.info("Matching Engine started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Matching Engine...")
    if matching_engine:
        await matching_engine.shutdown()
    logger.info("Matching Engine shutdown complete")

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
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "GoQuant Matching Engine",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check with engine status."""
    if matching_engine:
        return {
            "status": "healthy",
            "engine_status": "running",
            "supported_symbols": list(matching_engine.get_supported_symbols()),
            "active_orders": matching_engine.get_total_active_orders()
        }
    return {"status": "unhealthy", "engine_status": "not_initialized"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
