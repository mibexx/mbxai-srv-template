from typing import Any
from mcp.server.fastmcp import FastMCP

from models.request import WeatherInput

# Create a FastMCP instance for this module
mcp = FastMCP("weather")

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