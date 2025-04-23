"""Project-level API endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional

# Create a router for project-level endpoints
router = APIRouter(prefix="/project", tags=["project"])


class HelloRequest(BaseModel):
    """Hello world request model."""
    name: str = Field("World", description="Name to greet")


class HelloResponse(BaseModel):
    """Hello world response model."""
    message: str
    name: str


@router.post("/hello", response_model=HelloResponse)
async def hello_world(request: HelloRequest) -> HelloResponse:
    """A simple hello world endpoint.
    
    This is an example of a project-level endpoint that is automatically
    included in the main API.
    """
    return HelloResponse(
        message=f"Hello, {request.name}!",
        name=request.name,
    ) 