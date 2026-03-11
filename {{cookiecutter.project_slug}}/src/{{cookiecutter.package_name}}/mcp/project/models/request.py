from typing import Any

from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    location: str
    units: str = "celsius"  # Default to celsius, can be "fahrenheit" or "celsius"
    auth: dict[str, Any] | None = Field(
        default=None,
        description="Authentication context injected by the MCP server",
        alias="__auth__",
        serialization_alias="__auth__",
    )
