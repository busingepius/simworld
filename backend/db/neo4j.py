import sys
from typing import Optional, Any
from neo4j import AsyncGraphDatabase, AsyncDriver

from core.config import get_settings
from core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

class Neo4jClient:
    """
    Singleton client for Neo4j async database connections.
    """
    _instance: Optional['Neo4jClient'] = None
    
    def __new__(cls) -> 'Neo4jClient':
        if cls._instance is None:
            cls._instance = super(Neo4jClient, cls).__new__(cls)
            cls._instance._driver = None
        return cls._instance

    def __init__(self):
        # Prevent re-initialization if already created
        if getattr(self, '_initialized', False):
            return
            
        try:
            self._driver: AsyncDriver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_lifetime=3600,
                max_connection_pool_size=50,
                connection_timeout=10.0,
            )
            self._initialized = True
        except Exception as e:
            logger.error("neo4j_initialisation_failed", error=str(e), exc_info=sys.exc_info())
            raise

    async def close(self) -> None:
        """Close the Neo4j driver connection."""
        if self._driver is not None:
            await self._driver.close()
            self._driver = None

    async def verify_connectivity(self) -> bool:
        """Verify that the driver can communicate with the server."""
        if self._driver is None:
            return False
        try:
            await self._driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error("neo4j_connectivity_failed", error=str(e))
            return False

    def get_driver(self) -> AsyncDriver:
        """Get the underlying AsyncDriver instance."""
        if self._driver is None:
            raise RuntimeError("Neo4j driver is not initialized or was closed.")
        return self._driver

def get_neo4j() -> Neo4jClient:
    """Return the Neo4j singleton client."""
    return Neo4jClient()
