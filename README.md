# MIBEXX AI Service Template

A cookiecutter template for creating AI Services that can be launched in the Mibexx AI Orchestrator to expose ai features.

## Features

- FastAPI for REST API implementation
- Pydantic for data validation
- SQLAlchemy for ORM
- Alembic for database migrations
- Docker support
- Testing with pytest
- Type checking with mypy
- Code linting with ruff
- Modern Python 3.12+ features
- OpenRouter API client with tool and agent support

## Usage

```bash
cookiecutter gh:mibexx/mbxai-srv-template
```

## Requirements

- Python 3.12+
- Cookiecutter 2.1.0+

## OpenRouter API Client Guide

The template includes a powerful OpenRouter API client that supports both chat completions and structured parsing, with advanced tool and agent capabilities.

### Basic Usage

```python
from {{cookiecutter.package_name}}.clients.openrouter import OpenRouterApiClient, OpenRouterModel

# Initialize the client
client = OpenRouterApiClient(model=OpenRouterModel.GPT_41)

# Simple chat completion
messages = [
    {"role": "user", "content": "Tell me about Python programming language"}
]
response = await client.chat_completion(messages)
print(response["content"])

# Structured output with chat_parse
from pydantic import BaseModel, Field
from typing import list

class ProgrammingLanguage(BaseModel):
    name: str = Field(..., description="The name of the programming language")
    description: str = Field(..., description="A brief description of the language")
    features: list[str] = Field(..., description="Key features of the language")

structured_output = ProgrammingLanguage
response = await client.chat_parse(
    messages,
    structured_output=structured_output
)
print(response["parsed"])
```

### Using Tools

The client supports registering and using tools with the OpenRouter API:

```python
import json
from typing import Any

# Define tool schemas
search_schema = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query"
        }
    },
    "required": ["query"]
}

summarize_schema = {
    "type": "object",
    "properties": {
        "text": {
            "type": "string",
            "description": "The text to summarize"
        },
        "max_length": {
            "type": "integer",
            "description": "Maximum length of the summary"
        }
    },
    "required": ["text"]
}

# Define tool handlers
async def search_handler(args: dict[str, Any]) -> Any:
    query = args["query"]
    # Implement your search logic here
    return f"Search results for: {query}"

async def summarize_handler(args: dict[str, Any]) -> Any:
    text = args["text"]
    max_length = args.get("max_length", 100)
    # Implement your summarization logic here
    return f"Summary of {text[:max_length]}..."

# Register tools
client.register_tool("search", search_schema, search_handler)
client.register_tool("summarize", summarize_schema, summarize_handler)

# Use tools in chat completion
messages = [
    {"role": "user", "content": "Find information about Python and summarize it"}
]
response = await client.chat_completion(
    messages,
    call_tools=True  # Enable tool calling
)
print(response["content"])
print("Tool calls:", response["tool_calls"])
```

### Using the Agent Mode

The client supports an agent mode that can execute multiple rounds of tool calls:

```python
# Enable agent mode to automatically execute tools
response = await client.chat_completion(
    messages,
    call_tools=True,
    use_agent=True  # Enable agent mode
)
print(response["content"])
print("All tool calls:", response["tool_calls"])
print("All tool results:", response["tool_results"])
```

### Advanced Agent Usage

The agent can handle complex workflows with multiple rounds of tool calls:

```python
# Define a more complex tool schema
web_search_schema = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query"
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return"
        }
    },
    "required": ["query"]
}

data_analysis_schema = {
    "type": "object",
    "properties": {
        "data": {
            "type": "string",
            "description": "The data to analyze"
        },
        "analysis_type": {
            "type": "string",
            "enum": ["sentiment", "keywords", "summary"],
            "description": "Type of analysis to perform"
        }
    },
    "required": ["data", "analysis_type"]
}

# Register the tools
client.register_tool("web_search", web_search_schema, web_search_handler)
client.register_tool("analyze_data", data_analysis_schema, analyze_data_handler)

# Use the agent with a complex task
messages = [
    {"role": "user", "content": "Search for recent news about AI, analyze the sentiment of the results, and summarize the key points"}
]

# The agent will:
# 1. Call web_search to find news
# 2. Call analyze_data with sentiment analysis on the results
# 3. Call analyze_data with summary on the results
# 4. Provide a final response
response = await client.chat_completion(
    messages,
    call_tools=True,
    use_agent=True
)
print(response["content"])
```

### Tool Choice Control

You can control which tools the model can use:

```python
# Set tool choice to "auto" (default)
client.set_tool_choice("auto")

# Set tool choice to "none" to disable tool calling
client.set_tool_choice("none")

# Set tool choice to a specific tool
client.set_tool_choice("search")

# Override tool choice for a specific request
response = await client.chat_completion(
    messages,
    call_tools=True,
    tool_choice="summarize"  # Override for this request only
)
```

### Structured Output with Tools

You can combine structured output with tools:

```python
class ResearchSummary(BaseModel):
    topic: str = Field(..., description="The research topic")
    findings: list[str] = Field(..., description="Key findings from the research")
    sources: list[str] = Field(..., description="Sources of information")

structured_output = ResearchSummary.model_json_schema()
response = await client.chat_parse(
    messages,
    structured_output=structured_output,
    call_tools=True,
    use_agent=True
)
print(response["parsed"])
```
