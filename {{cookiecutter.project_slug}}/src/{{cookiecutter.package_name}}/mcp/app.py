from collections.abc import Mapping
from typing import Any

from mbxai.mcp.server import MCPServer, OAuth2Configuration

from ..config import get_config, get_mcp_oauth2_config
from .auth import get_oauth2_router

config = get_config()
oauth2_config_settings = get_mcp_oauth2_config()


def _build_oauth2_configuration() -> OAuth2Configuration | None:
    """Create an OAuth2Configuration if all required values are present."""
    if (
        not oauth2_config_settings.issuer
        or not oauth2_config_settings.authorization_endpoint
        or not oauth2_config_settings.token_endpoint
        or not oauth2_config_settings.jwks_uri
    ):
        return None

    return OAuth2Configuration(
        issuer=oauth2_config_settings.issuer,
        authorization_endpoint=oauth2_config_settings.authorization_endpoint,
        token_endpoint=oauth2_config_settings.token_endpoint,
        jwks_uri=oauth2_config_settings.jwks_uri,
        scopes_supported=oauth2_config_settings.scopes_supported,
    )


async def validate_oauth2_token(
    token: str,
    required_scopes: list[str],
) -> dict[str, object]:
    """Validate the OAuth2 token and return an authentication context.

    This is a placeholder implementation. Replace this function with logic
    that validates the token and scopes against your Identity Provider.
    """
    return {
        "access_token": token,
        "scopes": required_scopes,
    }


oauth2_configuration = _build_oauth2_configuration()

# Import the tools
from .project.weather import get_weather


def _build_server() -> MCPServer:
    """Create the MCPServer with optional OAuth2 support."""
    server_kwargs: dict[str, object] = {
        "name": config.name,
    }

    if oauth2_configuration is not None:
        server_kwargs["oauth2_configuration"] = oauth2_configuration
        server_kwargs["oauth2_handler"] = validate_oauth2_token

    return MCPServer(**server_kwargs)


# Initialize mbxai server
server = _build_server()

# Get the FastAPI app from the mbxai server
app = server.app

# Mount the simple OAuth2 endpoints (can be replaced or extended in projects)
app.include_router(get_oauth2_router())


# Function to register tools
async def register_tools():
    """Register all tools with the server."""
    security_schemes: list[Mapping[str, Any]] | None = None

    if oauth2_configuration is not None and oauth2_configuration.scopes_supported:
        security_schemes = [
            {
                "type": "oauth2",
                "scopes": oauth2_configuration.scopes_supported,
            },
        ]

    if security_schemes:
        await server.add_tool(
            get_weather,
            security_schemes=security_schemes,
        )
    else:
        await server.add_tool(get_weather)

