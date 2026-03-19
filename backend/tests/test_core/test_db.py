import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db, engine
from db.neo4j import Neo4jClient, get_neo4j

@pytest.mark.asyncio
async def test_get_db_yields_session():
    # Test that get_db yields an AsyncSession and correctly calls close
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.__aenter__.return_value = mock_session
    
    with patch("db.session.AsyncSessionFactory", return_value=mock_session):
        gen = get_db()
        session = await anext(gen)
        assert session is mock_session
        
        # Advance generator to trigger cleanup
        try:
            await anext(gen)
        except StopAsyncIteration:
            pass
            
        # Verify close was called
        mock_session.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_db_rollback_on_exception():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.__aenter__.return_value = mock_session
    
    with patch("db.session.AsyncSessionFactory", return_value=mock_session):
        gen = get_db()
        session = await anext(gen)
        
        # Simulate exception inside the context manager
        with pytest.raises(ValueError):
            await gen.athrow(ValueError("Test error"))
            
        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()

@patch("db.neo4j.AsyncGraphDatabase.driver")
def test_neo4j_singleton(mock_driver):
    # Reset singleton if it exists
    Neo4jClient._instance = None
    
    mock_driver.return_value = MagicMock()
    
    client1 = get_neo4j()
    client2 = get_neo4j()
    
    assert client1 is client2
    # Ensure driver is only created once
    mock_driver.assert_called_once()

@pytest.mark.asyncio
@patch("db.neo4j.AsyncGraphDatabase.driver")
async def test_neo4j_verify_connectivity(mock_driver):
    Neo4jClient._instance = None
    
    mock_driver_instance = AsyncMock()
    mock_driver.return_value = mock_driver_instance
    
    client = get_neo4j()
    
    # Test success
    result = await client.verify_connectivity()
    assert result is True
    mock_driver_instance.verify_connectivity.assert_awaited_once()
    
    # Test failure
    mock_driver_instance.verify_connectivity.side_effect = Exception("Connection error")
    result = await client.verify_connectivity()
    assert result is False

@pytest.mark.asyncio
@patch("db.neo4j.AsyncGraphDatabase.driver")
async def test_neo4j_close(mock_driver):
    Neo4jClient._instance = None
    mock_driver_instance = AsyncMock()
    mock_driver.return_value = mock_driver_instance
    
    client = get_neo4j()
    await client.close()
    
    mock_driver_instance.close.assert_awaited_once()
    assert client._driver is None
