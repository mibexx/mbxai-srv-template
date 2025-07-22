from pydantic import BaseModel, Field

class HelloRequest(BaseModel):
    """Hello world request model."""
    name: str = Field("World", description="Name to greet")

class WeatherRequest(BaseModel):
    """Weather request model."""
    location: str = Field(..., description="Location to get weather for")