"""
Configuration settings for the GoQuant Matching Engine.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Matching engine configuration
    MAX_ORDER_SIZE: float = 1000000.0  # Maximum order size
    MIN_ORDER_SIZE: float = 0.00000001  # Minimum order size
    MAX_PRICE: float = 1000000.0  # Maximum price
    MIN_PRICE: float = 0.00000001  # Minimum price
    
    # Supported trading pairs
    SUPPORTED_SYMBOLS: List[str] = [
        "BTC-USDT", "ETH-USDT", "BNB-USDT", "ADA-USDT", "SOL-USDT",
        "XRP-USDT", "DOT-USDT", "DOGE-USDT", "AVAX-USDT", "MATIC-USDT"
    ]
    
    # Order book configuration
    MAX_ORDER_BOOK_LEVELS: int = 1000  # Maximum levels in order book
    ORDER_BOOK_PRECISION: int = 8  # Decimal precision for prices
    
    # Performance configuration
    MAX_ORDERS_PER_SECOND: int = 10000
    BATCH_SIZE: int = 100  # Orders processed in batch
    
    # Logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "matching_engine.log"
    
    # Database configuration (for persistence)
    DATABASE_URL: str = "sqlite:///./matching_engine.db"
    
    # Redis configuration (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
