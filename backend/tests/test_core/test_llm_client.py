import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from pydantic import BaseModel
import httpx

from core.llm_client import complete, complete_structured
from core.exceptions import LLMCallFailedError

class DummySchema(BaseModel):
    name: str
    age: int

@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        yield mock_instance

@pytest.mark.asyncio
async def test_complete_success(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello, world!"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    }
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = await complete(prompt="Say hi", system="Be nice", context_id="test-run")
    assert result == "Hello, world!"

    mock_httpx_client.post.assert_awaited_once()
    args, kwargs = mock_httpx_client.post.call_args
    assert "json" in kwargs
    assert kwargs["json"]["messages"][0]["role"] == "system"
    assert kwargs["json"]["messages"][1]["role"] == "user"

@pytest.mark.asyncio
async def test_complete_http_error(mock_httpx_client):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"error": "Invalid API key"}
    
    # raise_for_status raises HTTPStatusError
    mock_error = httpx.HTTPStatusError("401 error", request=AsyncMock(), response=mock_response)
    mock_response.raise_for_status.side_effect = mock_error
    mock_httpx_client.post.return_value = mock_response

    with pytest.raises(LLMCallFailedError) as exc_info:
        await complete(prompt="Say hi")
        
    assert "401" in str(exc_info.value)
    assert exc_info.value.detail["status_code"] == 401

@pytest.mark.asyncio
async def test_complete_structured_success(mock_httpx_client):
    mock_response = MagicMock()
    # Mocking a JSON string response wrapped in markdown block
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "```json\n{\"name\": \"Alice\", \"age\": 30}\n```"}}],
        "usage": {}
    }
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    result = await complete_structured(prompt="Who is Alice?", response_schema=DummySchema)
    
    assert isinstance(result, DummySchema)
    assert result.name == "Alice"
    assert result.age == 30

@pytest.mark.asyncio
async def test_complete_structured_parse_error(mock_httpx_client):
    mock_response = MagicMock()
    # Mocking invalid JSON
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "This is not JSON"}}],
        "usage": {}
    }
    mock_response.raise_for_status.return_value = None
    mock_httpx_client.post.return_value = mock_response

    with pytest.raises(LLMCallFailedError) as exc_info:
        await complete_structured(prompt="Who is Alice?", response_schema=DummySchema)
        
    assert "parse" in str(exc_info.value).lower()
