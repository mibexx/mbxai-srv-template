# MIBEXX AI Service Template

A template for creating AI services with FastAPI, Pydantic, SQLAlchemy, and Docker support.

## Features

- FastAPI for high-performance API development
- Pydantic for data validation and settings management
- SQLAlchemy for database operations
- Docker support for containerization
- OpenRouter API client for AI model interactions
- Model Context Protocol (MCP) client for tool discovery and execution
- Comprehensive testing setup with pytest
- Code quality tools: mypy, ruff
- GitHub Actions for CI/CD

## Configuration

The service requires the following environment variables:

### Application Configuration

These variables are prefixed with `{{cookiecutter.project_slug.upper()}}_`:

- `{{cookiecutter.project_slug.upper()}}_NAME`: Name of your service (default: "{{cookiecutter.project_name}}")
- `{{cookiecutter.project_slug.upper()}}_VERSION`: Version of your service (default: package version)
- `{{cookiecutter.project_slug.upper()}}_LOG_LEVEL`: Logging level (default: 20 for INFO)

### AI Service Configuration

- `OPENROUTER_TOKEN`: Your OpenRouter API token for AI model interactions
- `OPENROUTER_BASE_URL`: Base URL for OpenRouter API (default: "https://openrouter.ai/api/v1")
- `MCP_SERVER_URL`: URL of the Model Context Protocol server (optional)

These can be set in your environment or in a `.env` file in the project root.

## Project Structure

The template creates a well-organized project structure:

```
{{cookiecutter.project_slug}}/
├── src/
│   └── {{cookiecutter.package_name}}/
│       ├── api/                  # Core API functionality
│       │   ├── definition.py     # API definition generation
│       │   ├── run.py            # Server startup
│       │   └── server.py         # FastAPI server configuration
│       ├── clients/              # Client libraries
│       │   ├── mcp.py            # Model Context Protocol client
│       │   ├── models.py         # Model definitions
│       │   └── openrouter.py     # OpenRouter API client
│       ├── project/              # Project-specific code
│       │   └── api.py            # Project API endpoints
│       ├── config.py             # Configuration management
│       └── __init__.py           # Package initialization
├── tests/                        # Test suite
├── data/                         # Data storage
├── logs/                         # Log files
├── kubernetes/                   # Kubernetes deployment files
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
├── pyproject.toml                # Project metadata and dependencies
└── README.md                     # This file
```

## Usage

### Creating a New Project

```bash
cookiecutter gh:mibexx/mbxai-srv-template
```

Follow the prompts to configure your project.

### Installing Dependencies with uv

This project uses [uv](https://github.com/astral-sh/uv) for fast and reliable dependency management:

```bash
# Install uv if you don't have it already
pip install uv

# Install dependencies
uv sync

# Run the service
uv run service
```

Or with command-line arguments:

```bash
uv run service -- --host 127.0.0.1 --port 5000 --reload
```

### Running the Service

```bash
# Run the service
python -m src.{{cookiecutter.package_name}}.api.run
```

Or with command-line arguments:

```bash
python -m src.{{cookiecutter.package_name}}.api.run --host 127.0.0.1 --port 5000 --reload
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t {{cookiecutter.project_slug}} .

# Run the container
docker run -p 5000:5000 {{cookiecutter.project_slug}}
```

Or with docker-compose:

```bash
docker-compose up
```

### API Endpoints

The template includes several API endpoints:

- `GET /ident`: Returns basic service identity information
- `GET /mbxai-definition`: Returns the definition of all API endpoints
- Project-specific endpoints in the `/api` path

### AI Clients

The template includes two AI clients for different use cases:

1. **OpenRouter API Client** (`openrouter.py`): A direct client for the OpenRouter API that supports chat completions, structured output parsing, and tool execution.

2. **Model Context Protocol Client** (`mcp.py`): A client that implements the Model Context Protocol for tool discovery and execution, providing a more standardized approach to tool handling.

Both clients can be used independently or together, depending on your needs.

### OpenRouter API Client

The OpenRouter API client supports:

- Chat completions
- Structured output parsing
- Tool registration and execution
- Agent mode with multiple rounds of tool calls
- Streaming agent responses

#### Basic Usage

```python
from mbxai.clients.openrouter import OpenRouterApiClient, OpenRouterModel

# Initialize the client
client = OpenRouterApiClient()

# Send a message
response = await client.chat_completion(
    messages=[{"role": "user", "content": "Hello, world!"}]
)
print(response["content"])
```

#### Structured Output

```python
from pydantic import BaseModel

class UserInfo(BaseModel):
    name: str
    age: int

# Parse structured output
response = await client.chat_parse(
    messages=[{"role": "user", "content": "My name is John and I am 30 years old."}],
    structured_output=UserInfo
)
print(response["parsed"])  # UserInfo(name="John", age=30)
```

#### Tool Registration

```python
async def search_database(query: str) -> str:
    # Implement database search
    return f"Results for: {query}"

# Register a tool
client.register_tool(
    name="search_database",
    description="Search the database for information",
    function=search_database,
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"}
        },
        "required": ["query"]
    }
)
```

#### Agent Mode

```python
# Run an agent that can use tools
response = await client.agent(
    messages=[{"role": "user", "content": "Find information about John"}],
    max_iterations=5
)
print(response["content"])
print(response["tool_calls"])
print(response["tool_results"])
```

#### Streaming Agent Responses

```python
# Stream agent responses
async for step in client.agent_stream(
    messages=[{"role": "user", "content": "Find information about John"}]
):
    if step["is_final"]:
        print("Final response:", step["content"])
    else:
        print(f"Iteration {step['iteration']}:", step["content"])
        if step["tool_calls"]:
            print("Tool calls:", step["tool_calls"])
            print("Tool results:", step["tool_results"])
```

### Model Context Protocol (MCP) Client

The MCP client supports:

- Connecting to MCP servers
- Discovering tools from servers
- Executing tools through the MCP protocol
- Agent mode with MCP tools
- Streaming agent responses

#### Basic Usage

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

# Get available tools
tools = client.get_available_tools()
print("Available tools:", [tool["function"]["name"] for tool in tools])
```

#### Agent Mode with MCP Tools

```python
# Run an agent that can use MCP tools
response = await client.agent(
    messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
    max_iterations=5
)
print(response["content"])
print(response["tool_calls"])
print(response["tool_results"])
```

#### Streaming Agent Responses

```python
# Stream agent responses
async for step in client.agent_stream(
    messages=[{"role": "user", "content": "What's the weather like in Paris?"}]
):
    if step["is_final"]:
        print("Final response:", step["content"])
    else:
        print(f"Iteration {step['iteration']}:", step["content"])
        if step["tool_calls"]:
            print("Tool calls:", step["tool_calls"])
            print("Tool results:", step["tool_results"])
```

### Creating a Simple Tool

Here's an example of how to create a simple tool using the MCP approach:

#### 1. Create an MCP Server

```python
from mcp import Server, StdioServerTransport, Tool

# Create a server
server = Server("my-server")

# Define a tool
@server.tool()
async def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"The weather in {location} is sunny."

# Run the server
async def main():
    transport = StdioServerTransport()
    await server.serve(transport)

if __name__ == "__main__":
    asyncio.run(main())
```

#### 2. Use the Tool with the MCP Client

```python
from mcp import StdioServerParameters

# Create server parameters
server_params = StdioServerParameters(
    command=["python", "path/to/your/mcp_server.py"]
)

# Run an agent that uses the weather tool
response = await client.agent(
    messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
    max_iterations=3
)
print(response["content"])
```

#### 3. Create a Tool with the OpenRouter Client

```python
from mbxai.clients.openrouter import OpenRouterApiClient

# Initialize the client
client = OpenRouterApiClient()

# Define the tool handler
async def get_weather(query: str) -> str:
    location = query
    # In a real implementation, you would call a weather API
    return json.dumps({
        "location": location,
        "temperature": 22,
        "condition": "Sunny",
        "humidity": 65
    })

# Register the tool
client.register_tool(
    name="get_weather",
    description="Get the current weather for a location",
    function=get_weather,
    parameters={
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "The city and country, e.g. 'London, UK'"}
        },
        "required": ["location"]
    }
)

# Run an agent that uses the weather tool
response = await client.agent(
    messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
    max_iterations=3
)
print(response["content"])
```

## How to develop UI

The UI layer follows a clear separation of concerns architecture designed to provide a responsive frontend while keeping AI and backend logic properly organized.

### Architecture Overview

The UI architecture consists of three main layers:

1. **UI Layer** (`ui/app.py`): Flask-based frontend that serves HTML templates and handles user interactions
2. **Backend API Layer** (`api/`): FastAPI-based service that handles business logic and AI processing  
3. **Client Utilities** (`utils/client.py`): Provides standardized clients for AI and external service calls

### UI → Backend Communication

The UI should **never** make direct AI calls or handle complex business logic. Instead, follow this pattern:

```python
# In ui/app.py - Proxy pattern
@app.route('/api/your-endpoint', methods=['POST'])
@csrf.exempt
def your_endpoint_proxy():
    """Proxy the request to the backend API."""
    try:
        request_data = request.get_json()
        
        # Forward to backend API
        api_url = f"{config.API_URL}/api/your-endpoint"
        response = requests.post(
            api_url,
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=300
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Backend error'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Backend API Implementation

Your backend API endpoints should handle the actual business logic and AI processing:

```python
# In api/project/your_endpoints.py
from ...utils.client import get_mcp_client
from models.request import YourRequest
from models.response import YourResponse

@router.post("/your-endpoint", response_model=YourResponse)
async def your_endpoint(request: YourRequest) -> YourResponse:
    """Process your request with AI assistance."""
    try:
        # Get the MCP client for AI calls
        client = get_mcp_client()
        
        # Create messages for AI processing
        messages = [
            {
                "role": "user", 
                "content": f"Process this request: {request.your_field}"
            }
        ]
        
        # Use parse method with Pydantic model for structured output
        response = client.parse(
            messages=messages,
            response_format=YourResponse,
        )
        
        # Return the parsed response
        return response.choices[0].message.parsed
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Configuration and Client Usage

#### Using API_URL for Backend Calls

The UI uses `API_URL` from config to communicate with the backend:

```python
# In ui/app.py
config = get_ui_config()
api_url = f"{config.API_URL}/api/your-endpoint"
```

#### Using utils.client for External Services

For calling external services or other AI services, use the client utilities:

```python
# For AI calls - Always use McpClient
from ...utils.client import get_mcp_client

client = get_mcp_client()
response = client.parse(
    messages=messages,
    response_format=YourPydanticModel,
)

# For other service calls
from ...utils.client import ServiceApiClient

service_client = ServiceApiClient()
result = await service_client.call_service(
    namespace="your-namespace",
    service_name="service-name", 
    endpoint="endpoint-name",
    data={"key": "value"}
)
```

### AI Integration Best Practices

#### 1. Always Use McpClient for AI Calls

```python
# ✅ Correct way
client = get_mcp_client()
response = client.parse(
    messages=[{"role": "user", "content": "Your prompt"}],
    response_format=YourResponseModel,
)
result = response.choices[0].message.parsed
```

#### 2. Define Proper Pydantic Models

```python
# In models/response.py
from pydantic import BaseModel
from typing import Optional

class YourResponse(BaseModel):
    """Response model for your endpoint."""
    result: str
    confidence: Optional[float] = None
    metadata: Optional[dict] = None
```

#### 3. Handle Errors Gracefully

```python
try:
    response = client.parse(
        messages=messages,
        response_format=YourResponse,
    )
    
    if not response or not response.choices:
        raise ValueError("Empty response from AI")
        
    if not hasattr(response.choices[0].message, "parsed"):
        raise ValueError("No parsed response from AI")
        
    return response.choices[0].message.parsed
    
except Exception as e:
    logger.error(f"AI processing failed: {str(e)}")
    raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")
```

### Frontend JavaScript Integration

For frontend interactions, use standard AJAX calls to your UI proxy endpoints:

```javascript
// In your JavaScript files
async function callBackendAPI(endpoint, data) {
    try {
        const response = await fetch(`/api/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token  // Get from template context
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Usage
const result = await callBackendAPI('your-endpoint', {
    field1: 'value1',
    field2: 'value2'
});
```

### Development Workflow

1. **Design your data models** in `models/request.py` and `models/response.py`
2. **Implement backend logic** in `api/project/` with proper AI integration using `McpClient`
3. **Create UI proxy endpoints** in `ui/app.py` that forward requests to backend
4. **Build frontend templates** with JavaScript that calls your proxy endpoints
5. **Test the full flow** from UI → Proxy → Backend API → AI Service

### Example: Complete Implementation

See `api/project/demo.py` for a complete example that demonstrates:
- Proper use of `get_mcp_client()`
- Using `client.parse()` with Pydantic models
- Error handling and response processing
- Integration with the UI layer

This architecture ensures clean separation of concerns, maintainable code, and proper handling of AI services while keeping the UI responsive and user-friendly.

## Development

### Testing

```bash
pytest
```

### Linting

```bash
ruff check .
```

### Type Checking

```bash
mypy src
```

## Requirements

- Python 3.12+
- Cookiecutter 2.5.0+

## License

This project is licensed under the MIT License - see the LICENSE file for details.
