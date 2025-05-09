from ..config import get_openrouter_api_config, get_mcp_config

from mbxai.openrouter import OpenRouterModel, OpenRouterClient
from mbxai.mcp import MCPClient
from mbxai.tools import ToolClient

def get_openrouter_client(model: OpenRouterModel = OpenRouterModel.GPT41) -> OpenRouterClient:
    """Get the OpenRouter client."""
    return OpenRouterClient(api_key=get_openrouter_api_config().api_key, base_url=get_openrouter_api_config().base_url, model=model)

def get_tool_client(model: OpenRouterModel = OpenRouterModel.GPT41) -> ToolClient:
    """Get the Tool client."""
    return ToolClient(get_openrouter_client(model))

def get_mcp_client(model: OpenRouterModel = OpenRouterModel.GPT41) -> MCPClient:
    """Get the MCP client."""
    mcp_client = MCPClient(get_openrouter_client(model))
    
    mcp_config = get_mcp_config()
    if mcp_config.server_url:
        mcp_client.register_mcp_server("mcp-server", mcp_config.server_url)
    
    return mcp_client
