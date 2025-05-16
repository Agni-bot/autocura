# Data Schemas for Data Interface Module
# Defines the structure for various data types used in the system.

from typing import TypedDict, List, Optional, Union

# Using TypedDict for basic schema definition. 
# In a more complex system, Pydantic or similar validation libraries would be preferred.

class MarketDataSchema(TypedDict):
    symbol: str
    price: float
    volume: int
    timestamp: str # ISO 8601 format, e.g., "YYYY-MM-DDTHH:MM:SSZ"
    bid: Optional[float]
    ask: Optional[float]

class GeospatialDataSchema(TypedDict):
    sensor_id: str
    data_type: str # e.g., "weather", "shipping_traffic", "port_congestion"
    value: Union[str, float, dict]
    location: Optional[str] # e.g., "port_xyz", "lat_long_coords"
    timestamp: str # ISO 8601 format

class OrderSchema(TypedDict):
    order_id: str
    symbol: str
    order_type: str # e.g., "LIMIT", "MARKET"
    side: str # e.g., "BUY", "SELL"
    quantity: float
    price: Optional[float] # Required for LIMIT orders
    status: str # e.g., "NEW", "FILLED", "CANCELLED"
    timestamp: str # ISO 8601 format
    # Fields for anonymization techniques if needed at this level
    anonymization_details: Optional[dict]

# Example of how these might be used (not part of the schemas themselves)
if __name__ == '__main__':
    sample_market_data: MarketDataSchema = {
        "symbol": "EUR/USD",
        "price": 1.0850,
        "volume": 1000000,
        "timestamp": "2025-05-09T09:45:00Z",
        "bid": 1.0849,
        "ask": 1.0851
    }
    print(f"Sample Market Data: {sample_market_data}")

    sample_geo_data: GeospatialDataSchema = {
        "sensor_id": "SAT_WEATHER_001",
        "data_type": "weather_pattern",
        "value": {"condition": "storm_approaching", "region": "North Atlantic"},
        "location": "45.0000N_30.0000W",
        "timestamp": "2025-05-09T09:00:00Z"
    }
    print(f"Sample Geospatial Data: {sample_geo_data}")

    sample_order: OrderSchema = {
        "order_id": "ORD123456789",
        "symbol": "USD/JPY",
        "order_type": "LIMIT",
        "side": "BUY",
        "quantity": 50000,
        "price": 155.25,
        "status": "NEW",
        "timestamp": "2025-05-09T09:45:00Z"
    }
    print(f"Sample Order: {sample_order}")

