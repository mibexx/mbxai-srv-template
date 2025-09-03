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
from your_package.utils.client import get_openrouter_client
from mbxai.openrouter import OpenRouterModel

# Initialize the client
client = get_openrouter_client(model=OpenRouterModel.GPT_41)

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
    response_format=UserInfo
)
print(response.choices[0].message.parsed)  # UserInfo(name="John", age=30)
```

### Tool Client

The ToolClient provides the same interface as OpenRouterClient but with enhanced tool capabilities. It supports the same `chat` and `parse` methods:

```python
from your_package.utils.client import get_tool_client
from mbxai.openrouter import OpenRouterModel
from pydantic import BaseModel

# Initialize the client
client = get_tool_client(model=OpenRouterModel.GPT_41)

# Simple chat completion
response = await client.chat(
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
print(response.choices[0].message.content)

# Chat completion with structured output
class UserInfo(BaseModel):
    name: str
    age: int

response = await client.parse(
    messages=[
        {"role": "user", "content": "My name is John and I am 30 years old."}
    ],
    response_format=UserInfo
)
print(response.choices[0].message.parsed)  # UserInfo(name="John", age=30)
```

### Model Context Protocol (MCP) Client

The MCP Client is a child class of ToolClient and inherits the same `chat` and `parse` methods. It provides enhanced capabilities for tool and agent handling and can connect to MCP servers.

#### Basic Usage

The MCP Client uses the same interface as ToolClient:

```python
from your_package.utils.client import get_mcp_client
from mbxai.openrouter import OpenRouterModel
from pydantic import BaseModel

# Initialize the client (automatically connects to configured MCP servers)
client = get_mcp_client(model=OpenRouterModel.GPT_41)

# Simple chat completion (same as ToolClient)
response = await client.chat(
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
print(response.choices[0].message.content)

# Chat completion with structured output (same as ToolClient)
class WeatherInfo(BaseModel):
    location: str
    temperature: float
    conditions: str

response = await client.parse(
    messages=[
        {"role": "user", "content": "What's the weather in New York?"}
    ],
    response_format=WeatherInfo
)
print(response.choices[0].message.parsed)  # WeatherInfo(location="New York", ...)
```

#### Advanced MCP Features

```python
# Get available tools from connected MCP servers
tools = client.get_available_tools()
print(f"Available tools: {[tool['function']['name'] for tool in tools]}")

# The client automatically uses MCP tools when making chat/parse requests
response = await client.parse(
    messages=[
        {"role": "user", "content": "Get the current weather in Paris"}
    ],
    response_format=WeatherInfo
)
```

#### MCP Client Features

The MCP client provides the following features:

- **Inherits ToolClient**: All `chat` and `parse` methods work exactly like ToolClient
- **Automatic MCP Integration**: Automatically connects to configured MCP servers
- **Tool Discovery**: Automatically discovers tools from connected servers
- **Structured Output**: Full support for structured output using Pydantic models
- **Seamless Tool Usage**: Tools are automatically available in chat/parse calls

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

A weather endpoint that demonstrates how to use the MCP client to get weather information:

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

1. Uses the MCP client (which inherits from ToolClient)
2. Automatically connects to configured MCP servers
3. Uses the `parse` method with structured output to get weather information

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
