import pytest
import uuid
from unittest.mock import AsyncMock, patch

from core.scenario import convert_scenario_to_injections, ScenarioInjectionResult, MemoryInjection
from core.exceptions import SimWorldError

@pytest.fixture
def target_ids():
    return [uuid.uuid4(), uuid.uuid4()]

@pytest.fixture
def mock_injection_result(target_ids):
    return ScenarioInjectionResult(
        injections=[
            MemoryInjection(agent_id=target_ids[0], memory_text="You hear rumors of a new policy."),
            MemoryInjection(agent_id=target_ids[1], memory_text="A memo crosses your desk regarding recent changes.")
        ]
    )

@pytest.mark.asyncio
@patch("core.scenario.complete_structured")
async def test_convert_scenario_success(mock_complete, target_ids, mock_injection_result):
    mock_complete.return_value = mock_injection_result
    
    injections = await convert_scenario_to_injections(
        scenario_description="A new tax policy is enacted.",
        target_agent_ids=target_ids,
        strength=1.5
    )
    
    assert len(injections) == 2
    assert injections[0].agent_id == target_ids[0]
    assert "policy" in injections[0].memory_text
    
    mock_complete.assert_awaited_once()
    args, kwargs = mock_complete.call_args
    assert "tax policy" in kwargs["prompt"]

@pytest.mark.asyncio
async def test_convert_scenario_global():
    # When target_ids is empty, it should return early without calling the LLM
    with patch("core.scenario.complete_structured") as mock_complete:
        injections = await convert_scenario_to_injections(
            scenario_description="Global earthquake.",
            target_agent_ids=[]
        )
        
        assert len(injections) == 0
        mock_complete.assert_not_called()

@pytest.mark.asyncio
@patch("core.scenario.complete_structured")
async def test_convert_scenario_failure(mock_complete, target_ids):
    mock_complete.side_effect = Exception("LLM overloaded")
    
    with pytest.raises(SimWorldError) as exc_info:
        await convert_scenario_to_injections("A random event", target_ids)
        
    assert "Failed to convert scenario" in str(exc_info.value)
