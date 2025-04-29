from typing import Any

import httpx
from pydantic import BaseModel

from ..config import get_mcp_config


class ToolSchema(BaseModel):
    """Schema for a tool's input parameters."""
    properties: dict[str, Any]
    required: list[str]
    title: str
    type: str


class Tool(BaseModel):
    """Model representing a tool from the MCP server."""
    description: str
    inputSchema: ToolSchema
    internal_url: str
    name: str
    service: str


class ToolsResponse(BaseModel):
    """Response from the MCP server tools endpoint."""
    tools: list[Tool]


class MCPClient:
    """Client for interacting with MCP server tools."""

    def __init__(self) -> None:
        self.config = get_mcp_config()
        if not self.config.server_url:
            raise ValueError("MCP server URL not configured. Set MCP_SERVER_URL environment variable.")
        self.base_url = self.config.server_url.rstrip("/")

    async def get_tools(self) -> list[Tool]:
        """Get all available tools from the MCP server."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/tools")
            response.raise_for_status()
            return ToolsResponse.model_validate(response.json()).tools

    async def invoke_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Invoke a specific tool by name with the given parameters."""
        tools = await self.get_tools()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")

        async with httpx.AsyncClient() as client:
            response = await client.post(tool.internal_url, json=kwargs)
            response.raise_for_status()
            return response.json() 