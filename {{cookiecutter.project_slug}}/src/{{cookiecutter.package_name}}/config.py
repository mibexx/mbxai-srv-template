import importlib.metadata
import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent.parent
SERVICE_NAME = "{{cookiecutter.project_slug.upper()}}_"


def _get_version() -> str:
    """Get the package version."""
    try:
        return importlib.metadata.version("{{cookiecutter.package_name}}")
    except importlib.metadata.PackageNotFoundError:
        return "0.1.0"  # Default during development


class ApplicationConfig(BaseSettings):
    """Application configuration."""

    name: str = "{{cookiecutter.project_name}}"
    version: str = Field(default_factory=_get_version)
    log_level: int = logging.INFO

    model_config = SettingsConfigDict(
        env_prefix=SERVICE_NAME,
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
class UiConfig(BaseSettings):
    
    APP_NAME: str = "{{cookiecutter.project_name}}"
    DEBUG: bool = False
    TESTING: bool = False
    
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # API Configuration for connecting to the CSV2JSON API
    API_URL: str = Field(default="http://localhost:5000")
    
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

class OpenRouterAPIConfig(BaseSettings):
    """OpenRouter API configuration."""

    api_key: str = Field(alias="OPENROUTER_TOKEN")
    base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class MCPConfig(BaseSettings):
    """MCP server configuration."""

    server_url: str | None = Field(default=None, alias="MCP_SERVER_URL")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

class ServiceAPIConfig(BaseSettings):
    """Service API configuration."""

    api_url: str = Field(default="https://api.mbxai.cloud/api", alias="MBXAI_API_URL")
    token: str = Field(default="", alias="MBXAI_API_TOKEN")
    service_namespace: str = Field(default="mbxai-srv", alias="SERVICE_NAMESPACE")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    
class OpenAIConfig(BaseSettings):
    """OpenAI API configuration."""

    api_key: str = Field(alias="OPENAI_API_KEY")
    embedding_model: str = Field(default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL")
    organization: str | None = Field(default=None, alias="OPENAI_ORGANIZATION")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ChromaDBConfig(BaseSettings):
    """ChromaDB configuration."""

    persist_directory: str = Field(default="./chroma_db", alias="CHROMA_PERSIST_DIRECTORY")
    host: str | None = Field(default=None, alias="CHROMA_HOST")
    port: int | None = Field(default=None, alias="CHROMA_PORT")
    ssl: bool = Field(default=False, alias="CHROMA_SSL")
    headers: dict[str, str] | None = Field(default=None, alias="CHROMA_HEADERS")
    
    # Authentication settings
    auth_token: str | None = Field(default=None, alias="CHROMA_AUTH_TOKEN")
    auth_token_type: str = Field(default="Bearer", alias="CHROMA_AUTH_TOKEN_TYPE")
    
    # Collection settings
    default_collection_name: str = Field(default="default_collection", alias="CHROMA_DEFAULT_COLLECTION")
    default_distance_function: str = Field(default="cosine", alias="CHROMA_DISTANCE_FUNCTION")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_config() -> ApplicationConfig:
    """Get the application configuration singleton."""
    return ApplicationConfig()

@lru_cache
def get_ui_config() -> UiConfig:
    """Get the application configuration singleton."""
    return UiConfig()


@lru_cache
def get_openrouter_api_config() -> OpenRouterAPIConfig:
    """Get the OpenRouter API configuration singleton."""
    return OpenRouterAPIConfig()


@lru_cache
def get_mcp_config() -> MCPConfig:
    """Get the MCP configuration singleton."""
    return MCPConfig()

@lru_cache
def get_service_api_config() -> ServiceAPIConfig:
    """Get the service api configuration singleton."""
    return ServiceAPIConfig()


@lru_cache
def get_openai_config() -> OpenAIConfig:
    """Get the OpenAI configuration singleton."""
    return OpenAIConfig()


@lru_cache
def get_chromadb_config() -> ChromaDBConfig:
    """Get the ChromaDB configuration singleton."""
    return ChromaDBConfig()