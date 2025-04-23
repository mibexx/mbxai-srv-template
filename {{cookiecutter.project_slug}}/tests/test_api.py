"""Tests for the API endpoints."""

import json
from fastapi.testclient import TestClient

from src.{{cookiecutter.package_name}}.api import app
from src.{{cookiecutter.package_name}}.config import get_config
from src.{{cookiecutter.package_name}}.api.echo import EchoRequest, EchoResponse
from src.{{cookiecutter.package_name}}.project.api import HelloRequest

client = TestClient(app)

def test_ident_endpoint():
    """Test the /ident endpoint returns correct data."""
    response = client.get("/ident")
    assert response.status_code == 200
    
    config = get_config()
    data = response.json()
    
    assert data["name"] == config.name
    assert data["version"] == config.version

def test_echo_endpoint():
    """Test the /echo endpoint correctly processes requests."""
    # Define test data
    test_message = "Hello, world!"
    test_count = 3
    
    # Create request
    echo_request = EchoRequest(message=test_message, count=test_count)
    
    # Send request
    response = client.post(
        "/echo",
        json=echo_request.model_dump(),
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Validate response data
    assert data["response"] == test_message * test_count
    assert data["request_length"] == len(test_message)

def test_project_hello_endpoint():
    """Test the project-level /project/hello endpoint."""
    # Test with default name
    hello_request = HelloRequest()
    response = client.post(
        "/project/hello",
        json=hello_request.model_dump(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Hello, World!"
    assert data["name"] == "World"
    
    # Test with custom name
    custom_name = "Tester"
    hello_request = HelloRequest(name=custom_name)
    response = client.post(
        "/project/hello",
        json=hello_request.model_dump(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Hello, {custom_name}!"
    assert data["name"] == custom_name

def test_mbxai_definition_endpoint():
    """Test the /mbxai-definition endpoint returns API definitions."""
    response = client.get("/mbxai-definition")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check that it's a list
    assert isinstance(data, list)
    
    # Check that it contains at least the echo endpoint
    echo_endpoint = next((d for d in data if d["endpoint"] == "/echo"), None)
    assert echo_endpoint is not None
    assert echo_endpoint["method"] == "POST"
    
    # Check that project endpoint is included
    project_endpoint = next((d for d in data if d["endpoint"] == "/project/hello"), None)
    assert project_endpoint is not None
    assert project_endpoint["method"] == "POST"
    
    # Check that excluded endpoints are not included
    endpoints = [d["endpoint"] for d in data]
    assert "/ident" not in endpoints
    assert "/mbxai-definition" not in endpoints 