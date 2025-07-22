"""Project-level API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import Optional

from ...utils.client import get_openrouter_client
from models.request import HelloRequest, WeatherRequest
from models.response import HelloResponse, WeatherResponse

# Create a router for project-level endpoints
router = APIRouter(prefix="/api", tags=["api"])


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


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
    """Get weather information for a location using OpenAI with MCP tools.
    
    This endpoint uses the MCP client to connect to an MCP server and
    uses OpenAI to process the weather request using available tools.
    """
    try:
        # Initialize MCP client and connect to server
        client = get_openrouter_client()

        # Create the prompt for OpenAI
        messages = [
            {
                "role": "user",
                "content": f"Give me the weather for {request.location}"
            }
        ]

        # Use the agent to get weather information
        response = client.create(
            messages=messages,
            max_iterations=3  # Limit iterations since we just need one tool call
        )

        return WeatherResponse(weather_info=response.choices[0].message.content)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather: {str(e)}") 