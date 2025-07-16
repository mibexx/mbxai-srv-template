from typing import Any
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

# Create a FastMCP instance for this module
mcp = FastMCP("weather")

class WeatherInput(BaseModel):
    location: str
    units: str = "celsius"  # Default to celsius, can be "fahrenheit" or "celsius"

@mcp.tool()
async def get_weather(input: WeatherInput) -> dict[str, Any]:
    """Get weather information for a location.
    
    Args:
        input: WeatherInput model containing location and units preference
    """
    # This is a mock implementation
    temperature = 20 if input.units == "celsius" else 68  # Convert to fahrenheit if needed
    
    return {
        "location": input.location,
        "temperature": temperature,
        "units": input.units,
        "condition": "sunny",
        "humidity": 65,
    }