"""Vector storage utilities for managing ChromaDB collections with OpenAI embeddings."""

import logging
from typing import Any

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI

from ..config import ChromaDBConfig, OpenAIConfig, get_chromadb_config, get_openai_config

logger = logging.getLogger(__name__)


def _convert_list_metadata_for_chromadb(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Convert list values in metadata to comma-separated strings for ChromaDB compatibility.
    
    ChromaDB metadata only supports scalar values (string, int, float, bool).
    This function converts list values to comma-separated strings.
    
    Args:
        metadata: Original metadata dictionary that may contain lists
        
    Returns:
        Metadata dictionary with lists converted to comma-separated strings
    """
    converted_metadata = {}
    
    for key, value in metadata.items():
        if isinstance(value, list):
            # Convert list to comma-separated string
            converted_metadata[key] = ", ".join(str(item) for item in value)
        else:
            # Keep non-list values as-is
            converted_metadata[key] = value
    
    return converted_metadata


class ChromaCollectionManager:
    """
    A utility class for managing ChromaDB collections with OpenAI embeddings.
    
    This class provides a clean interface for creating, retrieving, listing,
    and deleting collections in ChromaDB using OpenAI's embedding models.
    """

    def __init__(
        self,
        chromadb_config: ChromaDBConfig | None = None,
        openai_config: OpenAIConfig | None = None,
    ) -> None:
        """
        Initialize the ChromaDB collection manager.
        
        Args:
            chromadb_config: ChromaDB configuration. If None, loads from environment.
            openai_config: OpenAI configuration. If None, loads from environment.
        """
        self._chromadb_config = chromadb_config or get_chromadb_config()
        self._openai_config = openai_config or get_openai_config()
        
        self._client = self._initialize_client()
        self._embedding_function = self._initialize_embedding_function()

    def _initialize_client(self) -> chromadb.ClientAPI:
        """Initialize the ChromaDB client based on configuration."""
        if self._chromadb_config.host and self._chromadb_config.port:
            # Remote ChromaDB instance
            logger.info(
                f"Connecting to remote ChromaDB at "
                f"{'https' if self._chromadb_config.ssl else 'http'}://"
                f"{self._chromadb_config.host}:{self._chromadb_config.port}"
            )
            
            # Prepare headers with authentication if provided
            headers = self._chromadb_config.headers or {}
            if self._chromadb_config.auth_token:
                auth_header = f"{self._chromadb_config.auth_token_type} {self._chromadb_config.auth_token}"
                headers["Authorization"] = auth_header
                logger.info("Using authentication token for ChromaDB connection")
            
            return chromadb.HttpClient(
                host=self._chromadb_config.host,
                port=self._chromadb_config.port,
                ssl=self._chromadb_config.ssl,
                headers=headers,
            )
        else:
            # Local persistent ChromaDB instance
            logger.info(f"Using local ChromaDB at {self._chromadb_config.persist_directory}")
            return chromadb.PersistentClient(
                path=self._chromadb_config.persist_directory,
                settings=Settings(anonymized_telemetry=False),
            )

    def _initialize_embedding_function(self) -> embedding_functions.OpenAIEmbeddingFunction:
        """Initialize the OpenAI embedding function."""
        return embedding_functions.OpenAIEmbeddingFunction(
            api_key=self._openai_config.api_key,
            model_name=self._openai_config.embedding_model,
            organization_id=self._openai_config.organization,
        )

    def create_collection(
        self,
        name: str,
        metadata: dict[str, Any] | None = None,
        get_or_create: bool = True,
    ) -> chromadb.Collection:
        """
        Create a new collection with OpenAI embeddings.
        
        Args:
            name: Name of the collection to create.
            metadata: Optional metadata for the collection.
            get_or_create: If True, get existing collection if it exists.
                          If False, raise error if collection exists.
        
        Returns:
            The created or retrieved collection.
            
        Raises:
            ValueError: If collection exists and get_or_create is False.
        """
        logger.info(f"Creating collection: {name}")
        
        # Convert list metadata values to comma-separated strings for ChromaDB compatibility
        if metadata:
            metadata = _convert_list_metadata_for_chromadb(metadata)
        
        try:
            if get_or_create:
                collection = self._client.get_or_create_collection(
                    name=name,
                    embedding_function=self._embedding_function,
                    metadata=metadata or {},
                )
                logger.info(f"Collection '{name}' created or retrieved successfully")
            else:
                collection = self._client.create_collection(
                    name=name,
                    embedding_function=self._embedding_function,
                    metadata=metadata or {},
                )
                logger.info(f"Collection '{name}' created successfully")
                
            return collection
            
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            raise

    def get_collection(self, name: str) -> chromadb.Collection:
        """
        Get an existing collection by name.
        
        Args:
            name: Name of the collection to retrieve.
            
        Returns:
            The collection object.
            
        Raises:
            ValueError: If collection doesn't exist.
        """
        logger.info(f"Retrieving collection: {name}")
        
        try:
            collection = self._client.get_collection(
                name=name,
                embedding_function=self._embedding_function,
            )
            logger.info(f"Collection '{name}' retrieved successfully")
            return collection
            
        except Exception as e:
            logger.error(f"Failed to retrieve collection '{name}': {e}")
            raise

    def list_collections(self) -> list[chromadb.Collection]:
        """
        List all available collections.
        
        Returns:
            List of all collections.
        """
        logger.info("Listing all collections")
        
        try:
            collections = self._client.list_collections()
            logger.info(f"Found {len(collections)} collections")
            return collections
            
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise

    def delete_collection(self, name: str) -> None:
        """
        Delete a collection by name.
        
        Args:
            name: Name of the collection to delete.
            
        Raises:
            ValueError: If collection doesn't exist.
        """
        logger.info(f"Deleting collection: {name}")
        
        try:
            self._client.delete_collection(name=name)
            logger.info(f"Collection '{name}' deleted successfully")
            
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            raise

    def collection_exists(self, name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            name: Name of the collection to check.
            
        Returns:
            True if collection exists, False otherwise.
        """
        try:
            self.get_collection(name)
            return True
        except Exception:
            return False

    def get_default_collection(self) -> chromadb.Collection:
        """
        Get the default collection as specified in configuration.
        
        Returns:
            The default collection.
        """
        return self.get_collection(self._chromadb_config.default_collection_name)

    def create_default_collection(
        self,
        metadata: dict[str, Any] | None = None,
    ) -> chromadb.Collection:
        """
        Create the default collection as specified in configuration.
        
        Args:
            metadata: Optional metadata for the collection.
            
        Returns:
            The default collection.
        """
        return self.create_collection(
            name=self._chromadb_config.default_collection_name,
            metadata=metadata,
            get_or_create=True,
        )

    @property
    def client(self) -> chromadb.ClientAPI:
        """Get the underlying ChromaDB client."""
        return self._client

    @property
    def embedding_function(self) -> embedding_functions.OpenAIEmbeddingFunction:
        """Get the OpenAI embedding function."""
        return self._embedding_function


def create_collection_manager(
    chromadb_config: ChromaDBConfig | None = None,
    openai_config: OpenAIConfig | None = None,
) -> ChromaCollectionManager:
    """
    Factory function to create a ChromaCollectionManager instance.
    
    Args:
        chromadb_config: Optional ChromaDB configuration. Uses environment if None.
        openai_config: Optional OpenAI configuration. Uses environment if None.
        
    Returns:
        A configured ChromaCollectionManager instance.
        
    Example:
        >>> manager = create_collection_manager()
        >>> collection = manager.create_collection("my_documents")
        >>> collection.add(documents=["Hello world"], ids=["1"])
    """
    return ChromaCollectionManager(
        chromadb_config=chromadb_config,
        openai_config=openai_config,
    )
