# {{cookiecutter.project_name}}

{{cookiecutter.description}}

## Features

- FastAPI-based REST API
- Configuration via environment variables and .env files
- Identity endpoint at `/ident`
- Command-line arguments for server configuration
- OpenRouter AI API client with retry logic and structured output support
- Configurable OpenRouter models through a dedicated models module
- Kubernetes deployment via MbxAiResource CustomResource
- Automatic API definition generation via `/mbxai-definition` endpoint
- Project-level API organization for better code structure
- Standardized Pydantic models for all requests and responses

## Installation

This project uses uv for dependency management.

```bash
uv sync
```

## Usage

Run the service with:

```bash
uv run service
```

Or with command-line arguments:

```bash
uv run service -- --host 127.0.0.1 --port 5000 --reload --workers 2
```

## API Endpoints

### GET /ident

Returns basic service identity information:

```json
{
  "name": "{{cookiecutter.project_name}}",
  "version": "0.1.0"
}
```

### POST /echo

Sample endpoint for testing that echoes the provided message:

Request:

```json
{
  "message": "Hello, world!",
  "count": 3
}
```

Response:

```json
{
  "response": "Hello, world!Hello, world!Hello, world!",
  "request_length": 13
}
```

### POST /api/hello

Project-level hello world endpoint demonstrating the use of FastAPI routers and Pydantic models:

Request:

```json
{
  "name": "World"
}
```

Response:

```json
{
  "message": "Hello, World!",
  "name": "World"
}
```

### GET /mbxai-definition

Returns the definition of all API endpoints, including their paths, methods, request schemas, and response schemas. This is useful for automatic client generation and documentation.

Example response:

```json
[
  {
    "endpoint": "/echo",
    "method": "POST",
    "request_schema": {
      "title": "EchoRequest",
      "type": "object",
      "properties": {
        "message": {
          "title": "Message",
          "type": "string",
          "description": "Message to echo back"
        },
        "count": {
          "title": "Count",
          "type": "integer",
          "description": "Number of times to repeat the message",
          "default": 1
        }
      },
      "required": ["message"]
    },
    "response_schema": {
      "title": "EchoResponse",
      "type": "object",
      "properties": {
        "response": {
          "title": "Response",
          "type": "string",
          "description": "Echoed message"
        },
        "request_length": {
          "title": "Request Length",
          "type": "integer",
          "description": "Length of the original message"
        }
      },
      "required": ["response", "request_length"]
    }
  }
]
```

## Project Structure

The service is organized into several key directories:

- `src/{{cookiecutter.package_name}}/api/`: Core API functionality including the main FastAPI server
- `src/{{cookiecutter.package_name}}/project/`: Project-level API endpoints and business logic
- `src/{{cookiecutter.package_name}}/clients/`: Client libraries for external services (like OpenRouter)
- `config/`: Configuration files
- `data/`: Data storage directory
- `logs/`: Log files

To add new project-level endpoints:

1. Define your API in `src/{{cookiecutter.package_name}}/project/api.py` or create new modules
2. The router is automatically included in the main API

## Configuration

Configuration is handled through environment variables with the prefix `{{cookiecutter.project_slug.upper()}}_` and through `.env` files in the project root.

Available settings:

- `NAME`: Service name (default: "{{cookiecutter.project_name}}")
- `VERSION`: Service version (default: package version or 0.1.0)
- `LOG_LEVEL`: Python logging level (default: 20 - INFO)

### OpenRouter Integration

This service includes a pre-configured OpenRouter API client. To use it, set the following environment variables:

```
{{cookiecutter.project_slug.upper()}}_OPENROUTER_API_KEY=your_api_key_here
{{cookiecutter.project_slug.upper()}}_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

Available models are defined in `src/{{cookiecutter.package_name}}/clients/models.py` and can be easily extended to add custom models.

Example:

```bash
export {{cookiecutter.project_slug.upper()}}_NAME="Custom Service Name"
export {{cookiecutter.project_slug.upper()}}_LOG_LEVEL=10  # DEBUG
uv run service
```

Or in a `.env` file:

```
{{cookiecutter.project_slug.upper()}}_NAME=Custom Service Name
{{cookiecutter.project_slug.upper()}}_LOG_LEVEL=10
{{cookiecutter.project_slug.upper()}}_OPENROUTER_API_KEY=your_api_key_here
```

## Deployment

### Docker

Build and run the service with Docker:

```bash
docker build -t {{cookiecutter.project_slug}} .
docker run -p 5000:5000 {{cookiecutter.project_slug}}
```

Or use docker-compose:

```bash
docker-compose up
```

### Kubernetes

This service can be deployed to a Kubernetes cluster using the MbxAiResource CustomResource Definition:

```bash
kubectl apply -f kubernetes/mbxai-resource.yaml
```

The CustomResource automatically deploys the service with the appropriate configuration. Modify `kubernetes/mbxai-resource.yaml` to adjust deployment parameters.

## Development

{% if cookiecutter.use_ruff == 'y' %}

### Linting

```bash
ruff check .
```

{% endif %}

{% if cookiecutter.use_mypy == 'y' %}

### Type Checking

```bash
mypy src
```

{% endif %}

{% if cookiecutter.use_pytest == 'y' %}

### Testing

```bash
pytest
```

{% endif %}
