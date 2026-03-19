import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from workers.simulation import _process_simulation
from models.simulation_run import SimulationRun
from models.agent_persona import AgentPersona
from core.simulation import SimulationStateOutput

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    session.__aenter__.return_value = session
    return session

@pytest.fixture
def mock_run():
    return SimulationRun(
        id=uuid.uuid4(),
        world_id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        status="queued",
        rounds=5
    )

@pytest.fixture
def mock_agent():
    return AgentPersona(
        id=uuid.uuid4(),
        world_id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        name="Test",
        is_active=True
    )

@pytest.mark.asyncio
@patch("workers.simulation.AsyncSessionFactory")
@patch("workers.simulation.run_simulation")
@patch("workers.simulation.celery.send_task")
async def test_process_simulation_success(mock_send_task, mock_run_sim, mock_session_factory, mock_session, mock_run, mock_agent):
    mock_session_factory.return_value = mock_session
    
    # Setup fetch run
    mock_session.get.return_value = mock_run
    
    # Setup fetch agents
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_agent]
    mock_session.execute.return_value = mock_result
    
    # Setup run simulation output
    mock_run_sim.return_value = SimulationStateOutput(
        run_id=mock_run.id,
        opinion_distributions={},
        coalitions={},
        trending_topics={},
        raw_log="log"
    )
    
    await _process_simulation(str(mock_run.id))
    
    # Assert state updates
    assert mock_run.status == "complete"
    assert mock_session.add.call_count == 1 # Added SimulationState
    
    # Assert report task dispatched
    mock_send_task.assert_called_once()
    args, kwargs = mock_send_task.call_args
    assert args[0] == "workers.report.generate_run_report"

@pytest.mark.asyncio
@patch("workers.simulation.AsyncSessionFactory")
async def test_process_simulation_no_agents(mock_session_factory, mock_session, mock_run):
    mock_session_factory.return_value = mock_session
    mock_session.get.return_value = mock_run
    
    # Setup empty agents
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_session.execute.return_value = mock_result
    
    with pytest.raises(ValueError, match="No active agents"):
        await _process_simulation(str(mock_run.id))
        
    assert mock_run.status == "failed" # Rollback handling
