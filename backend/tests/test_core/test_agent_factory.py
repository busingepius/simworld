import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from core.agent_factory import (
    generate_personas_from_graph,
    AgentFactoryResult,
    AgentPersonaProfile,
    AgentPersonality,
    AgentStance
)
from core.exceptions import SimWorldError

@pytest.fixture
def mock_personas():
    return AgentFactoryResult(
        personas=[
            AgentPersonaProfile(
                name="Alice Test",
                personality=AgentPersonality(
                    openness=0.8, conscientiousness=0.5, extraversion=0.9,
                    agreeableness=0.7, neuroticism=0.2, background_story="A cheerful local."
                ),
                stances=[
                    AgentStance(topic="New Policy", sentiment=0.9, reasoning="Good for business")
                ],
                influence_score=0.6
            ),
            AgentPersonaProfile(
                name="Bob Test",
                personality=AgentPersonality(
                    openness=0.2, conscientiousness=0.9, extraversion=0.3,
                    agreeableness=0.4, neuroticism=0.8, background_story="A worried manager."
                ),
                stances=[
                    AgentStance(topic="New Policy", sentiment=-0.8, reasoning="Too much risk")
                ],
                influence_score=0.4
            )
        ]
    )

@pytest.mark.asyncio
@patch("core.agent_factory._fetch_graph_summary")
@patch("core.agent_factory.complete_structured")
async def test_generate_personas_success(mock_complete, mock_fetch_graph, mock_personas):
    mock_fetch_graph.return_value = "ENTITIES:\n- Alice\n- Bob"
    mock_complete.return_value = mock_personas
    
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    personas = await generate_personas_from_graph(world_id, org_id, count=2)
    
    assert len(personas) == 2
    assert personas[0].name == "Alice Test"
    assert personas[1].name == "Bob Test"
    
    mock_fetch_graph.assert_awaited_once_with(str(world_id), str(org_id))
    mock_complete.assert_awaited_once()

@pytest.mark.asyncio
@patch("core.agent_factory._fetch_graph_summary")
@patch("core.agent_factory.complete_structured")
async def test_generate_personas_truncates_to_count(mock_complete, mock_fetch_graph, mock_personas):
    mock_fetch_graph.return_value = ""
    # We ask for 1, but LLM returns 2
    mock_complete.return_value = mock_personas
    
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    personas = await generate_personas_from_graph(world_id, org_id, count=1)
    
    # Should be truncated to 1
    assert len(personas) == 1
    assert personas[0].name == "Alice Test"

@pytest.mark.asyncio
@patch("core.agent_factory._fetch_graph_summary")
async def test_generate_personas_failure(mock_fetch_graph):
    mock_fetch_graph.side_effect = Exception("DB Connection Error")
    
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    with pytest.raises(SimWorldError) as exc_info:
        await generate_personas_from_graph(world_id, org_id, count=2)
        
    assert "Failed to generate agent personas" in str(exc_info.value)
