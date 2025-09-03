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

## Asynchronous Job Processing with Celery

The template includes a Celery client for handling asynchronous jobs using RabbitMQ as the message broker and Redis as the result backend. This is useful for long-running tasks, background processing, and distributed computing.

### Configuration

The Celery integration requires RabbitMQ and Redis instances. Configure them using environment variables:

#### RabbitMQ Configuration

- `RABBITMQ_HOST`: RabbitMQ host (default: "localhost")
- `RABBITMQ_PORT`: RabbitMQ port (default: 5672)
- `RABBITMQ_USERNAME`: RabbitMQ username (default: "guest")
- `RABBITMQ_PASSWORD`: RabbitMQ password (default: "guest")
- `RABBITMQ_VHOST`: RabbitMQ virtual host (default: "/")
- `RABBITMQ_SSL`: Enable SSL connection (default: false)

#### Redis Configuration

- `REDIS_HOST`: Redis host (default: "localhost")
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (optional, no default - Redis has no password by default)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_SSL`: Enable SSL connection (default: false)

#### Celery Configuration

- `CELERY_TASK_SERIALIZER`: Task serializer (default: "json")
- `CELERY_RESULT_SERIALIZER`: Result serializer (default: "json")
- `CELERY_ACCEPT_CONTENT`: Accepted content types (default: ["json"])
- `CELERY_RESULT_EXPIRES`: Result expiration time in seconds (default: 3600)
- `CELERY_TIMEZONE`: Timezone (default: "UTC")
- `CELERY_ENABLE_UTC`: Enable UTC (default: true)
- `CELERY_TASK_TRACK_STARTED`: Track task start (default: true)
- `CELERY_TASK_TIME_LIMIT`: Task time limit in seconds (default: 300)
- `CELERY_TASK_SOFT_TIME_LIMIT`: Soft task time limit in seconds (default: 240)

### Example Environment Configuration

For Kubernetes environments, you might configure:

```bash
# RabbitMQ (running in Kubernetes)
RABBITMQ_HOST=rabbitmq-service.default.svc.cluster.local
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=myuser
RABBITMQ_PASSWORD=mypassword

# Redis (running in Kubernetes, no password)
REDIS_HOST=redis-service.default.svc.cluster.local
REDIS_PORT=6379
```

### Usage

#### Importing the Client

```python
from {{cookiecutter.package_name}}.utils import CeleryClient, get_celery_client, send_task, get_task_result, get_task_status
```

#### Sending Messages (Tasks)

Use the client to send asynchronous tasks to workers:

```python
from {{cookiecutter.package_name}}.utils import get_celery_client

# Get the Celery client
client = get_celery_client()

# Send a task to be processed asynchronously
task_id = client.send_task(
    'my_app.tasks.process_data',  # Task name
    args=[1, 2, 3],               # Positional arguments
    kwargs={'option': 'value'},   # Keyword arguments
    queue='high_priority'         # Optional: specify queue
)

print(f"Task sent with ID: {task_id}")
```

#### Using Convenience Functions

For simple operations, use the convenience functions:

```python
from {{cookiecutter.package_name}}.utils import send_task, get_task_result, get_task_status

# Send a task
task_id = send_task('my_app.tasks.process_data', args=[1, 2, 3])

# Check task status
status = get_task_status(task_id)
print(f"Task status: {status}")  # PENDING, STARTED, SUCCESS, FAILURE, etc.

# Get task result (blocks until complete)
if status == 'SUCCESS':
    result = get_task_result(task_id, timeout=30)
    print(f"Result: {result}")
```

#### Receiving Messages (Creating Workers)

Create a Celery worker to process tasks. First, create your task functions:

```python
# In your_tasks.py
from {{cookiecutter.package_name}}.utils import get_celery_client

# Get the Celery app
celery_app = get_celery_client().app

@celery_app.task
def process_data(x, y, z, option=None):
    """Process some data asynchronously."""
    # Your processing logic here
    result = x + y + z
    if option:
        result = f"{result} with {option}"
    return result

@celery_app.task
def long_running_task(duration):
    """Simulate a long-running task."""
    import time
    time.sleep(duration)
    return f"Task completed after {duration} seconds"

@celery_app.task
def ai_processing_task(prompt):
    """Example AI processing task."""
    from {{cookiecutter.package_name}}.utils import get_mcp_client
    
    client = get_mcp_client()
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}]
    )
    return response["content"]
```

#### Running Workers

Start Celery workers to process tasks:

```bash
# Start a worker
celery -A your_tasks worker --loglevel=info

# Start a worker with specific queues
celery -A your_tasks worker --loglevel=info --queues=high_priority,low_priority

# Start multiple workers
celery -A your_tasks worker --loglevel=info --concurrency=4
```

#### Advanced Usage Examples

##### Task Management

```python
from {{cookiecutter.package_name}}.utils import get_celery_client

client = get_celery_client()

# Send task with custom options
task_id = client.send_task(
    'my_app.tasks.process_data',
    args=[1, 2, 3],
    kwargs={'option': 'value'},
    queue='high_priority',
    countdown=10,  # Delay execution by 10 seconds
    expires=300,   # Task expires after 5 minutes
    retry=True,    # Enable retries
    retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    }
)

# Get detailed task information
task_info = client.get_task_info(task_id)
print(f"Status: {task_info['status']}")
print(f"Result: {task_info['result']}")
if task_info['failed']:
    print(f"Error: {task_info['traceback']}")

# Revoke a task
if task_info['status'] == 'PENDING':
    client.revoke_task(task_id, terminate=True)
```

##### Monitoring and Management

```python
# Get active tasks across all workers
active_tasks = client.get_active_tasks()
for worker, tasks in active_tasks.items():
    print(f"Worker {worker}: {len(tasks)} active tasks")

# Get scheduled tasks
scheduled_tasks = client.get_scheduled_tasks()

# Check worker status
workers = client.ping_workers()
online_workers = [name for name, response in workers.items() if response == 'pong']
print(f"Online workers: {online_workers}")

# Purge a queue (remove all pending tasks)
purged_count = client.purge_queue('low_priority')
print(f"Purged {purged_count} messages from queue")
```

##### Task Registration

You can also register tasks dynamically:

```python
from {{cookiecutter.package_name}}.utils import get_celery_client

client = get_celery_client()

# Register a task function
@client.register_task(name='dynamic.task')
def my_dynamic_task(data):
    return f"Processed: {data}"

# Or register with automatic naming
@client.register_task
def another_task(x, y):
    return x * y
```

### Integration with FastAPI

You can integrate Celery tasks with your FastAPI endpoints:

```python
# In api/project/tasks.py
from fastapi import APIRouter, HTTPException
from {{cookiecutter.package_name}}.utils import send_task, get_task_status, get_task_result
from models.request import TaskRequest
from models.response import TaskResponse

router = APIRouter()

@router.post("/submit-task", response_model=TaskResponse)
async def submit_task(request: TaskRequest):
    """Submit a task for asynchronous processing."""
    try:
        task_id = send_task(
            'my_app.tasks.process_data',
            args=[request.data],
            kwargs={'option': request.option}
        )
        return TaskResponse(task_id=task_id, status='PENDING')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task-status/{task_id}")
async def task_status(task_id: str):
    """Get the status of a task."""
    try:
        status = get_task_status(task_id)
        result = None
        
        if status == 'SUCCESS':
            result = get_task_result(task_id)
        
        return {
            "task_id": task_id,
            "status": status,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Best Practices

1. **Task Design**: Keep tasks idempotent and stateless
2. **Error Handling**: Implement proper retry logic and error handling
3. **Resource Management**: Use connection pooling and limit task concurrency
4. **Monitoring**: Monitor queue lengths, worker health, and task execution times
5. **Security**: Use proper authentication for RabbitMQ and Redis in production
6. **Scaling**: Scale workers based on queue length and processing requirements

### Production Deployment

For production deployments:

1. Use dedicated RabbitMQ and Redis instances
2. Configure SSL/TLS for secure communication
3. Set up monitoring with tools like Flower or Celery Events
4. Use process managers like systemd or supervisor for worker processes
5. Implement proper logging and alerting

### Troubleshooting

Common issues and solutions:

- **Connection errors**: Check RabbitMQ/Redis connectivity and credentials
- **Task not executing**: Verify worker is running and listening to correct queues
- **Memory issues**: Monitor worker memory usage and restart workers periodically
- **Queue buildup**: Scale workers or optimize task processing

### Running Workers

The service includes a Celery worker for processing asynchronous tasks.

#### Local Development

```bash
# Run the worker locally
uv run worker
```

#### Example Tasks

The template includes example tasks in `worker/tasks.py`:

```python
# Example usage in your application
from {{cookiecutter.package_name}}.utils import send_task

# Send a simple task
task_id = send_task(
    '{{cookiecutter.package_name}}.worker.tasks.example_task',
    kwargs={'data': {'user_id': 123, 'action': 'process'}}
)

# Send an AI processing task
ai_task_id = send_task(
    '{{cookiecutter.package_name}}.worker.tasks.ai_processing_task',
    kwargs={'prompt': 'Analyze this data...'}
)
```

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
