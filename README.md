# MIBEXX AI Service Template

A comprehensive template for creating AI-powered services with FastAPI, integrated AI clients, and production-ready infrastructure.

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [AI Clients Reference](#ai-clients-reference)
- [Project Setup](#project-setup)
- [API Usage Examples](#api-usage-examples)
- [Configuration](#configuration)
- [Requirements](#requirements)

## Quick Start

### 1. Create New Project

```bash
uv tool run cookiecutter gh:mibexx/mbxai-srv-template
```

### 2. Basic AI Client Usage

```python
from your_package.utils.client import get_mcp_client
from pydantic import BaseModel

# Initialize AI client
client = get_mcp_client()

# Define response structure
class WeatherInfo(BaseModel):
    location: str
    temperature: float
    conditions: str

# Get structured AI response
response = await client.parse(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    response_format=WeatherInfo
)

result = response.choices[0].message.parsed
print(f"Weather: {result.temperature}°F, {result.conditions}")
```

### 3. Setup and Run the Service

```bash
cd your-project

# Install dependencies
uv sync

# Run the API service
uv run python -m your_package.api.run

# Or run other services
uv run python -m your_package.mcp.run    # MCP server
uv run python -m your_package.ui.app     # Web UI
uv run python -m your_package.worker.run # Background worker
```

## Features

### Core Infrastructure
- **FastAPI** - High-performance async API framework
- **Pydantic** - Data validation and settings management
- **SQLAlchemy** - Database operations with ORM
- **Docker** - Complete containerization support

### AI Integration
- **OpenRouter Client** - Direct AI model access
- **Tool Client** - Enhanced AI with tool capabilities
- **MCP Client** - Model Context Protocol integration
- **Structured Output** - Type-safe AI responses with Pydantic

### Development Tools
- **Testing** - Comprehensive pytest setup
- **Type Checking** - mypy integration
- **Code Quality** - ruff linting and formatting
- **CI/CD** - GitHub Actions workflows

## AI Clients Reference

### Client Architecture

```
OpenRouterClient (core AI client)
    ↓ (init param for)
ToolClient (wraps OpenRouterClient, adds tools)
    ↓ (inherited by)
MCPClient (inherits ToolClient, adds MCP integration)

AgentClient (separate wrapper)
    ↓ (can wrap any of)
OpenRouterClient | ToolClient | MCPClient
```

**Architecture Pattern**: 
- **ToolClient**: Takes OpenRouterClient as init param, wraps its logic
- **MCPClient**: Inherits from ToolClient, adds MCP server capabilities  
- **AgentClient**: Separate wrapper that can take any AI client for intelligent processing

### OpenRouterClient

**Methods:** `create()`, `parse()`
**Use Case:** Direct AI model interactions

```python
from your_package.utils.client import get_openrouter_client

client = get_openrouter_client()

# Basic chat
response = client.create(
    messages=[{"role": "user", "content": "Hello!"}]
)

# Structured output
response = await client.parse(
    messages=[{"role": "user", "content": "Extract name and age"}],
    response_format=UserInfo
)
```

### ToolClient

**Methods:** `chat()`, `parse()`
**Use Case:** AI with custom tool capabilities
**Architecture:** Wraps OpenRouterClient and delegates `parse()` calls

```python
from your_package.utils.client import get_tool_client

client = get_tool_client()

# Basic chat (delegates to OpenRouterClient.create internally)
response = client.chat(
    messages=[{"role": "user", "content": "Hello!"}]
)

# Structured output (delegates to OpenRouterClient.parse internally)
response = await client.parse(
    messages=[{"role": "user", "content": "Process this data"}],
    response_format=DataModel
)
```

### MCPClient (Recommended)

**Methods:** `chat()`, `parse()` (inherited from ToolClient)
**Use Case:** AI with automatic MCP tool integration
**Architecture:** Inherits from ToolClient, adds MCP server functionality

```python
from your_package.utils.client import get_mcp_client

client = get_mcp_client()

# Automatically uses available MCP tools
response = client.chat(
    messages=[{"role": "user", "content": "Get weather data"}]
)

# Structured output with tool usage
response = await client.parse(
    messages=[{"role": "user", "content": "Analyze this location"}],
    response_format=LocationAnalysis
)

# Check available tools
tools = client.get_available_tools()
```

### AgentClient

**Methods:** `agent()`
**Use Case:** Intelligent multi-step processing with automatic quality improvement
**Architecture:** Separate wrapper that can take any AI client as input parameter

```python
from your_package.utils.client import get_agent_client, get_mcp_client
from pydantic import BaseModel, Field

# Initialize agent with any AI client
ai_client = get_mcp_client()
agent = get_agent_client(ai_client, max_iterations=3)

# Define structured response
class TravelPlan(BaseModel):
    destination: str = Field(description="Travel destination")
    activities: list[str] = Field(description="Recommended activities")
    budget: str = Field(description="Estimated budget")

# Get intelligent response with automatic improvement
response = agent.agent(
    prompt="Plan a weekend trip to a mountain destination",
    final_response_structure=TravelPlan,
    ask_questions=False
)

# Access the improved result
plan = response.final_response
print(f"Destination: {plan.destination}")
print(f"Activities: {', '.join(plan.activities)}")
print(f"Budget: {plan.budget}")
```

#### AgentClient Features

- **Quality Improvement**: Automatically refines responses through multiple iterations
- **Structured Output**: Works with any Pydantic model for type-safe responses
- **Flexible Base**: Can wrap any AI client (OpenRouter, Tool, or MCP)
- **Configurable**: Set max_iterations to control processing depth
- **Question Mode**: Optional interactive questioning for clarification

### Method Comparison Table

| Client | Main Method | Parse Method | Tools | MCP Integration | Agent Processing | Architecture |
|--------|-------------|--------------|-------|-----------------|------------------|--------------|
| OpenRouterClient | `create()` | `parse()` | ❌ | ❌ | ❌ | Core AI client |
| ToolClient | `chat()` | `parse()` | ✅ | ❌ | ❌ | Wraps OpenRouterClient |
| MCPClient | `chat()` | `parse()` | ✅ | ✅ | ❌ | Inherits ToolClient |
| AgentClient | `agent()` | - | ✅* | ✅* | ✅ | Takes any AI client |

**Notes:** 
- All `parse()` calls ultimately delegate to `OpenRouterClient.parse()`
- *AgentClient inherits tools/MCP from the wrapped client

## Project Setup

### Project Structure

```
your-project/
├── src/your_package/
│   ├── api/                  # FastAPI application
│   │   ├── server.py         # Main FastAPI app
│   │   ├── run.py           # Application runner
│   │   └── project/         # Your API endpoints
│   ├── mcp/                 # MCP server implementation
│   ├── ui/                  # Web interface (optional)
│   ├── worker/              # Background tasks
│   ├── utils/               # Shared utilities
│   │   └── client.py        # AI client factories
│   └── config.py            # Configuration management
├── tests/                   # Test suite
├── docker-compose.yml       # Local development
├── Dockerfile              # Production container
└── pyproject.toml          # Dependencies & metadata
```

### Configuration Variables

Set these environment variables:

```bash
# Required
export MBXAI_OPENROUTER_API_KEY="your-api-key"

# Optional
export MBXAI_MCP_SERVER_URL="http://your-mcp-server"
export MBXAI_SERVICE_API_URL="http://your-service"
```

### Cookiecutter Options

When creating a project, configure:

- **project_name** - Display name
- **project_slug** - URL-safe identifier
- **package_name** - Python package name
- **description** - Brief description
- **author_name** - Your name
- **author_email** - Contact email
- **open_source_license** - License type
- **use_pytest** - Include testing (recommended: yes)
- **use_mypy** - Type checking (recommended: yes)
- **use_ruff** - Code quality (recommended: yes)

## API Usage Examples

### Hello World Endpoint

```bash
curl -X POST http://localhost:8000/api/hello \
  -H "Content-Type: application/json" \
  -d '{"name": "John"}'
```

Response:
```json
{"message": "Hello, John!", "name": "John"}
```

### AI-Powered Weather Endpoint

```bash
curl -X POST http://localhost:8000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"location": "London"}'
```

Response:
```json
{"weather_info": "Current weather in London: 18°C, partly cloudy"}
```

**How it works:**
1. Uses MCPClient with configured MCP servers
2. Automatically discovers and uses weather tools
3. Returns structured response via `parse()` method

### Custom Endpoint Pattern

```python
from fastapi import APIRouter
from your_package.utils.client import get_mcp_client
from pydantic import BaseModel

router = APIRouter()

class MyRequest(BaseModel):
    query: str

class MyResponse(BaseModel):
    result: str

@router.post("/my-endpoint", response_model=MyResponse)
async def my_endpoint(request: MyRequest) -> MyResponse:
    client = get_mcp_client()
    
    response = await client.parse(
        messages=[{"role": "user", "content": request.query}],
        response_format=MyResponse
    )
    
    return response.choices[0].message.parsed
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `MBXAI_OPENROUTER_API_KEY` | OpenRouter API key | Yes | - |
| `MBXAI_OPENROUTER_BASE_URL` | API base URL | No | OpenRouter default |
| `MBXAI_MCP_SERVER_URL` | MCP server endpoint | No | - |
| `MBXAI_SERVICE_API_URL` | Service API URL | No | - |
| `MBXAI_SERVICE_API_TOKEN` | Service API token | No | - |

### Client Configuration

```python
from mbxai.openrouter import OpenRouterModel
from your_package.utils.client import get_mcp_client, get_agent_client

# Different models
client = get_mcp_client(model=OpenRouterModel.GPT_41)      # GPT-4 Turbo
client = get_mcp_client(model=OpenRouterModel.CLAUDE_35)   # Claude 3.5
client = get_mcp_client(model=OpenRouterModel.GEMINI_PRO)  # Gemini Pro

# Agent configuration
ai_client = get_mcp_client(model=OpenRouterModel.GPT_41)
agent = get_agent_client(ai_client, max_iterations=5)      # More iterations for complex tasks
agent = get_agent_client(ai_client, max_iterations=1)      # Single iteration for simple tasks
```

## Requirements

- **Python 3.12+**
- **uv** (Python package manager) - Install with `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Cookiecutter 2.5.0+** - Install with `uv tool install cookiecutter`
- **OpenRouter API Key** (get one at [openrouter.ai](https://openrouter.ai))

## License

This project is licensed under the MIT License - see the LICENSE file for details.