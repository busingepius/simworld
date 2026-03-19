import json
from typing import Optional, Type, TypeVar, Any
from pydantic import BaseModel
import httpx

from core.config import get_settings
from core.exceptions import LLMCallFailedError
from core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

T = TypeVar("T", bound=BaseModel)

async def complete(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    context_id: Optional[str] = None,
) -> str:
    """
    Generate a text completion from the configured LLM provider.
    
    Returns the generated string.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model or settings.LLM_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Log usage for cost tracking if context is provided
            usage = data.get("usage", {})
            logger.info(
                "llm_call_success", 
                context_id=context_id, 
                model=payload["model"], 
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0)
            )
            
            return content

    except httpx.HTTPStatusError as e:
        error_detail = {"status_code": e.response.status_code, "context_id": context_id}
        try:
            error_detail["response_body"] = e.response.json()
        except ValueError:
            error_detail["response_body"] = e.response.text

        logger.error("llm_call_failed", error=str(e), **error_detail)
        raise LLMCallFailedError(f"LLM call failed with status {e.response.status_code}", detail=error_detail) from e
        
    except httpx.RequestError as e:
        error_detail = {"context_id": context_id, "url": str(e.request.url)}
        logger.error("llm_call_failed", error=str(e), **error_detail)
        raise LLMCallFailedError(f"LLM request error: {str(e)}", detail=error_detail) from e
    except Exception as e:
        logger.error("llm_call_failed", error=str(e), context_id=context_id)
        raise LLMCallFailedError(f"Unexpected LLM error: {str(e)}", detail={"context_id": context_id}) from e


async def complete_structured(
    prompt: str,
    response_schema: Type[T],
    system: Optional[str] = None,
    context_id: Optional[str] = None,
) -> T:
    """
    Generate a structured completion conforming to a Pydantic model.
    
    Returns an instance of the provided Pydantic model.
    """
    # Create a system prompt that includes the schema requirements
    schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
    
    system_instruction = system or "You are a helpful assistant."
    system_instruction += f"\n\nYou must respond ONLY with valid JSON that conforms to the following JSON Schema:\n{schema_json}"
    
    # We force temperature to 0 for structured data to be more deterministic
    raw_response = await complete(
        prompt=prompt,
        system=system_instruction,
        temperature=0.0,
        context_id=context_id
    )
    
    try:
        # Strip potential markdown code blocks
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        clean_json = clean_json.strip()
        
        # Parse and validate against the model
        parsed_dict = json.loads(clean_json)
        return response_schema.model_validate(parsed_dict)
    except json.JSONDecodeError as e:
        logger.error("llm_structured_parse_failed", error=str(e), raw_response=raw_response, context_id=context_id)
        raise LLMCallFailedError(f"Failed to parse LLM response as JSON: {str(e)}", detail={"context_id": context_id, "raw_response": raw_response}) from e
    except Exception as e:
        logger.error("llm_structured_validation_failed", error=str(e), raw_response=raw_response, context_id=context_id)
        raise LLMCallFailedError(f"Failed to validate structured LLM response: {str(e)}", detail={"context_id": context_id, "raw_response": raw_response}) from e