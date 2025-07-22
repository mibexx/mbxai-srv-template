from pydantic import BaseModel

class HelloResponse(BaseModel):
    """Hello world response model."""
    message: str
    name: str

class WeatherResponse(BaseModel):
    """Weather response model."""
    weather_info: str