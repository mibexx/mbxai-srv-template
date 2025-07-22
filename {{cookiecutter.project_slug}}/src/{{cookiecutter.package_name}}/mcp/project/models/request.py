from pydantic import BaseModel

class WeatherInput(BaseModel):
    location: str
    units: str = "celsius"  # Default to celsius, can be "fahrenheit" or "celsius"