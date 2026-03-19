import pytest
import uuid
import json
from unittest.mock import AsyncMock, patch

from core.simulation import run_simulation, SimulationStateOutput
from core.exceptions import SimWorldError, SimulationLimitExceededError
from models.agent_persona import AgentPersona

def create_mock_agent(name="Test Agent"):
    return AgentPersona(
        id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        world_id=uuid.uuid4(),
        name=name,
        personality={"background_story": "A generic test agent."},
        stance={"Test Topic": {"sentiment": 0.5, "reasoning": "Neutral"}},
        influence_score=0.5
    )

@pytest.fixture
def mock_agents():
    return [create_mock_agent("Alice"), create_mock_agent("Bob")]

@pytest.mark.asyncio
@patch("core.simulation.complete")
async def test_run_simulation_success(mock_complete, mock_agents):
    # Setup mock to return agent responses, then the analysis JSON
    def side_effect(*args, **kwargs):
        if "SIMULATION LOG" in kwargs.get("prompt", ""):
            return '{"opinion_distributions": {"topic": "split"}, "coalitions": {}, "trending_topics": {}}'
        return "I am reacting to this."
        
    mock_complete.side_effect = side_effect
    
    run_id = uuid.uuid4()
    world_id = uuid.uuid4()
    org_id = uuid.uuid4()
    
    result = await run_simulation(
        run_id=run_id,
        world_id=world_id,
        org_id=org_id,
        agents=mock_agents,
        rounds=2,
        scenario_injection="A new law is passed."
    )
    
    assert isinstance(result, SimulationStateOutput)
    assert result.run_id == run_id
    assert "A new law is passed" in result.raw_log
    assert "Alice: I am reacting to this" in result.raw_log
    assert result.opinion_distributions == {"topic": "split"}
    
    # 2 agents * 2 rounds + 1 analysis call = 5 calls
    assert mock_complete.call_count == 5

@pytest.mark.asyncio
async def test_run_simulation_zero_agents():
    with pytest.raises(SimWorldError) as exc:
        await run_simulation(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), agents=[])
    assert "0 agents" in str(exc.value)

@pytest.mark.asyncio
async def test_run_simulation_too_many_rounds(mock_agents):
    with pytest.raises(SimulationLimitExceededError) as exc:
        await run_simulation(uuid.uuid4(), uuid.uuid4(), uuid.uuid4(), agents=mock_agents, rounds=150)
    assert "exceeds the maximum" in str(exc.value)

@pytest.mark.asyncio
@patch("core.simulation.complete")
async def test_run_simulation_agent_failure_handled(mock_complete, mock_agents):
    # If an agent's LLM call fails, it shouldn't crash the whole simulation round
    def side_effect(*args, **kwargs):
        if "Alice" in kwargs.get("system", ""):
            raise Exception("API timeout")
        if "SIMULATION LOG" in kwargs.get("prompt", ""):
            return '{"opinion_distributions": {}, "coalitions": {}, "trending_topics": {}}'
        return "Bob reacts."
        
    mock_complete.side_effect = side_effect
    
    result = await run_simulation(
        run_id=uuid.uuid4(),
        world_id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        agents=mock_agents,
        rounds=1
    )
    
    assert "Alice: *remained silent*" in result.raw_log
    assert "Bob: Bob reacts." in result.raw_log
