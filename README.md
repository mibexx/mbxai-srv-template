# MIBEXX AI Service Template

A template for creating AI services with FastAPI, Pydantic, SQLAlchemy, and Docker support.

## Features

- FastAPI for high-performance API development
- Pydantic for data validation and settings management
- SQLAlchemy for database operations
- Docker support for containerization
- OpenRouter API client for AI model interactions
- Model Context Protocol (MCP) client for tool and agent handling
- Comprehensive testing setup with pytest
- Code quality tools: mypy, ruff
- GitHub Actions for CI/CD

## Usage

### Creating a New Project

```bash
cookiecutter gh:mibexx/mbxai-srv-template
```

Follow the prompts to configure your project:

- `project_name`: The name of your project
- `project_slug`: The slug for your project (used in paths and imports)
- `package_name`: The name of your Python package
- `description`: A short description of your project
- `author_name`: Your name
- `author_email`: Your email
- `open_source_license`: The license for your project
- `use_pytest`: Whether to include pytest for testing
- `use_mypy`: Whether to include mypy for type checking
- `use_ruff`: Whether to include ruff for linting

### Project Structure

The template creates a well-organized project structure:

```
your-project/
├── src/
│   └── your_package/
│       ├── api/                  # Core API functionality
│       ├── clients/              # Client libraries
│       ├── project/              # Project-specific code
│       ├── config.py             # Configuration management
│       └── __init__.py           # Package initialization
├── tests/                        # Test suite
├── data/                         # Data storage
├── logs/                         # Log files
├── kubernetes/                   # Kubernetes deployment files
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── pyproject.toml                # Project metadata and dependencies
└── README.md                     # Project documentation
```

## AI Clients

### OpenRouter API Client

The template includes an OpenRouter API client for interacting with AI models. Here's how to use it:

```python
from your_package.clients.openrouter import OpenRouterApiClient, OpenRouterModel

# Initialize the client
client = OpenRouterApiClient(model=OpenRouterModel.GPT_41)

# Simple chat completion
response = await client.create(
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
print(response.choices[0].message.content)

# Chat completion with structured output
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str
    age: int

response = await client.parse(
    messages=[
        {"role": "user", "content": "My name is John and I am 30 years old."}
    ],
    structured_output=UserInfo
)
print(response.choices[0].message.parsed)  # UserInfo(name="John", age=30)
```

### Model Context Protocol (MCP) Client

The template includes an MCP client for tool and agent handling. The MCP client can connect to both local and remote MCP servers.

#### Connecting to MCP Servers

```python
from your_package.clients.mcp import McpClient
from mcp import StdioServerParameters

# Initialize the client
client = McpClient()

# Connect to a local MCP server
server_params = StdioServerParameters(
    command=["python", "path/to/your/mcp_server.py"]
)
await client.add_mcp_server(server_params)

# Connect to a remote MCP server
await client.add_mcp_server("https://your-mcp-server.com/api/")

# Get available tools
tools = client.get_available_tools()
print(f"Available tools: {[tool['function']['name'] for tool in tools]}")
```

#### Using the MCP Client with an Agent

```python
from your_package.clients.mcp import McpClient
from pydantic import BaseModel

# Initialize the client and connect to MCP servers
client = McpClient()
await client.add_mcp_server("https://your-mcp-server.com/api/")

# Define a structured output for the agent
class WeatherInfo(BaseModel):
    location: str
    temperature: float
    conditions: str

# Run the agent with structured output
response = await client.agent(
    messages=[
        {"role": "user", "content": "What's the weather in New York?"}
    ],
    structured_output=WeatherInfo
)

# Access the parsed result and tool calls
print(f"Weather info: {response['parsed']}")
print(f"Tool calls: {response['tool_calls']}")
print(f"Tool results: {response['tool_results']}")

# Stream the agent's responses
async for step in client.agent_stream(
    messages=[
        {"role": "user", "content": "What's the weather in New York?"}
    ],
    structured_output=WeatherInfo
):
    print(f"Iteration {step['iteration']}: {step['parsed']}")
    if step['tool_calls']:
        print(f"Tool calls: {step['tool_calls']}")
    if step['tool_results']:
        print(f"Tool results: {step['tool_results']}")
    if step['is_final']:
        print("Agent completed")
```

#### MCP Client Features

The MCP client provides the following features:

- **Multiple Server Connections**: Connect to multiple MCP servers simultaneously
- **Automatic Tool Discovery**: Automatically discover tools from connected servers
- **Structured Output**: Support for structured output using Pydantic models
- **Agent Loop**: Run an agent that can use tools from connected servers
- **Streaming**: Stream the agent's responses as they are generated
- **Retry Logic**: Automatic retry for failed operations
- **Error Handling**: Comprehensive error handling for API calls and tool execution

## Project Endpoints

The template includes several project-level endpoints that demonstrate how to use the AI clients:

### Hello World Endpoint

A simple hello world endpoint that demonstrates basic FastAPI and Pydantic usage:

```bash
curl -X POST http://localhost:8000/api/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "John"}'
```

Response:

```json
{
  "message": "Hello, John!",
  "name": "John"
}
```

### Weather Endpoint

A weather endpoint that demonstrates how to use the MCP client with OpenAI to get weather information:

```bash
curl -X POST http://localhost:8000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}'
```

Response:

```json
{
  "weather_info": "The weather information for London..."
}
```

This endpoint:

1. Connects to an MCP server to discover available tools
2. Uses OpenAI to process the weather request
3. Lets OpenAI decide how to use the available tools to get weather information

To use this endpoint, you need to set the following environment variables:

```bash
export MBXAI_MCP_SERVER_URL="http://your-mcp-server"
export MBXAI_OPENROUTER_API_KEY="your-openrouter-api-key"
```

## Requirements

- Python 3.12+
- Cookiecutter 2.5.0+

## License

This project is licensed under the MIT License - see the LICENSE file for details.
