import pytest
import uuid
from unittest.mock import AsyncMock, patch

from core.report_agent import generate_report_from_state, GeneratedReport, ReportSection
from core.exceptions import SimWorldError
from models.simulation_state import SimulationState

@pytest.fixture
def mock_simulation_state():
    return SimulationState(
        id=uuid.uuid4(),
        org_id=uuid.uuid4(),
        world_id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        opinion_distributions={"policy_A": {"support": 0.8, "oppose": 0.2}},
        coalitions={"group_1": ["agent_A", "agent_B"]},
        trending_topics={"topics": ["economy"]},
        raw_log_path="local/path.txt"
    )

@pytest.fixture
def mock_report():
    return GeneratedReport(
        summary="The simulation indicates strong support for Policy A.",
        sections=[
            ReportSection(title="Key Findings", content="Economy is trending.")
        ],
        confidence_score=0.85
    )

@pytest.mark.asyncio
@patch("core.report_agent.complete_structured")
async def test_generate_report_success(mock_complete, mock_simulation_state, mock_report):
    mock_complete.return_value = mock_report
    
    run_id = uuid.uuid4()
    world_id = uuid.uuid4()
    
    report = await generate_report_from_state(run_id, world_id, mock_simulation_state)
    
    assert report.summary == mock_report.summary
    assert len(report.sections) == 1
    assert report.confidence_score == 0.85
    
    mock_complete.assert_awaited_once()
    args, kwargs = mock_complete.call_args
    assert "policy_A" in kwargs["prompt"]

@pytest.mark.asyncio
@patch("core.report_agent.complete_structured")
async def test_generate_report_failure(mock_complete, mock_simulation_state):
    mock_complete.side_effect = Exception("LLM connection lost")
    
    run_id = uuid.uuid4()
    world_id = uuid.uuid4()
    
    with pytest.raises(SimWorldError) as exc_info:
        await generate_report_from_state(run_id, world_id, mock_simulation_state)
        
    assert "Failed to generate report" in str(exc_info.value)
