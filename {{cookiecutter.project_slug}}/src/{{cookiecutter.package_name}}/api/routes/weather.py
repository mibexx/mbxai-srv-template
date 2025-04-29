from fastapi import APIRouter, HTTPException

from ...clients.mcp import McpClient
from ...config import get_mcp_config

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("/{location}")
async def get_weather(location: str) -> dict:
    """Get weather information for a location using the MCP weather tool."""
    try:
        mcp_config = get_mcp_config()
        if not mcp_config.server_url:
            raise HTTPException(
                status_code=500,
                detail="MCP server URL not configured. Set MCP_SERVER_URL environment variable."
            )

        client = McpClient()
        await client.add_http_mcp_server(mcp_config.server_url)
        return await client.invoke_tool("get_weather", location=location)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get weather: {str(e)}") 