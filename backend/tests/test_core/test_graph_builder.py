import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from core.graph_builder import (
    extract_graph_from_text, 
    build_graph_for_world,
    GraphExtraction, 
    Entity, 
    Relationship
)
from core.exceptions import SimWorldError

@pytest.fixture
def mock_extraction():
    return GraphExtraction(
        entities=[
            Entity(name="Alice", type="PERSON", attributes={"age": 30}),
            Entity(name="Bob", type="PERSON", attributes={"age": 35}),
        ],
        relationships=[
            Relationship(source="Alice", target="Bob", type="KNOWS", attributes={"since": 2020})
        ]
    )

@pytest.mark.asyncio
@patch("core.graph_builder.complete_structured")
async def test_extract_graph_from_text(mock_complete_structured, mock_extraction):
    mock_complete_structured.return_value = mock_extraction
    
    result = await extract_graph_from_text("Alice knows Bob.")
    
    assert len(result.entities) == 2
    assert result.entities[0].name == "Alice"
    assert result.relationships[0].type == "KNOWS"
    mock_complete_structured.assert_awaited_once()

@pytest.mark.asyncio
@patch("core.graph_builder.get_neo4j")
@patch("core.graph_builder.extract_graph_from_text")
async def test_build_graph_for_world_success(mock_extract, mock_get_neo4j, mock_extraction):
    mock_extract.return_value = mock_extraction
    
    mock_neo4j_client = MagicMock()
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    
    # Configure context manager for session
    mock_session.__aenter__.return_value = mock_session
    mock_driver.session.return_value = mock_session
    mock_neo4j_client.get_driver.return_value = mock_driver
    mock_get_neo4j.return_value = mock_neo4j_client
    
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    await build_graph_for_world(world_id, org_id, "Alice knows Bob.")
    
    mock_session.execute_write.assert_awaited_once()
    
    # Verify execute_write args (the transaction function and our context)
    args, kwargs = mock_session.execute_write.call_args
    tx_func = args[0]
    assert args[1] == str(world_id)
    assert args[2] == str(org_id)
    assert args[3] == mock_extraction

@pytest.mark.asyncio
@patch("core.graph_builder.get_neo4j")
@patch("core.graph_builder.extract_graph_from_text")
async def test_build_graph_for_world_empty_extraction(mock_extract, mock_get_neo4j):
    # Empty extraction
    mock_extract.return_value = GraphExtraction(entities=[], relationships=[])
    
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    await build_graph_for_world(world_id, org_id, "Nothing here.")
    
    # Neo4j should not be called
    mock_get_neo4j.assert_not_called()

@pytest.mark.asyncio
@patch("core.graph_builder.extract_graph_from_text")
async def test_build_graph_for_world_extraction_fails(mock_extract):
    mock_extract.side_effect = Exception("LLM failure")
    
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    with pytest.raises(SimWorldError) as exc_info:
        await build_graph_for_world(world_id, org_id, "Text")
        
    assert "LLM failure" in str(exc_info.value)
