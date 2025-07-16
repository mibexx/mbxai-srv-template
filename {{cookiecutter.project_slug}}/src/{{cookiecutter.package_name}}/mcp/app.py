from mbxai.mcp.server import MCPServer
from ..config import get_config

config = get_config()

# Import the tools
from ..project.mcp.weather import get_weather

# Initialize mbxai server
server = MCPServer(
    name=config.name,
    description=config.description
)

# Get the FastAPI app from the mbxai server
app = server.app

# Function to register tools
async def register_tools():
    """Register all tools with the server."""
    await server.add_tool(get_weather)
