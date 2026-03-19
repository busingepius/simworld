from core.exceptions import (
    SimWorldError,
    WorldNotFoundError,
    SimulationLimitExceededError,
    LLMCallFailedError
)

def test_base_sim_world_error():
    exc = SimWorldError("Something went wrong", {"run_id": "123"})
    assert str(exc) == "Something went wrong"
    assert exc.message == "Something went wrong"
    assert exc.detail == {"run_id": "123"}

def test_world_not_found_error():
    exc = WorldNotFoundError(detail={"world_id": "abc"})
    assert str(exc) == "World not found"
    assert exc.message == "World not found"
    assert exc.detail == {"world_id": "abc"}
    assert isinstance(exc, SimWorldError)

def test_simulation_limit_exceeded_error():
    exc = SimulationLimitExceededError("Agent limit reached", {"agent_count": 2000})
    assert exc.message == "Agent limit reached"
    assert exc.detail == {"agent_count": 2000}
    assert isinstance(exc, SimWorldError)

def test_llm_call_failed_error():
    exc = LLMCallFailedError("API timeout", {"provider": "openai"})
    assert exc.message == "API timeout"
    assert exc.detail == {"provider": "openai"}
    assert isinstance(exc, SimWorldError)
