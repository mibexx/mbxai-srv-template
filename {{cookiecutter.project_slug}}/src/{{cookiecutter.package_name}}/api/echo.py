"""Echo API endpoint module."""

from pydantic import BaseModel, Field
from typing import Optional


class EchoRequest(BaseModel):
    """Echo request model."""
    message: str = Field(..., description="Message to echo back")
    count: Optional[int] = Field(1, description="Number of times to repeat the message")


class EchoResponse(BaseModel):
    """Echo response model."""
    response: str = Field(..., description="Echoed message")
    request_length: int = Field(..., description="Length of the original message") 