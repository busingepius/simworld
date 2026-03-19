import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

from core.llm_client import complete_structured
from core.logging import get_logger
from core.exceptions import SimWorldError

logger = get_logger(__name__)

class MemoryInjection(BaseModel):
    agent_id: uuid.UUID = Field(..., description="The ID of the target agent")
    memory_text: str = Field(..., description="The text to inject into the agent's memory")

class ScenarioInjectionResult(BaseModel):
    injections: List[MemoryInjection] = Field(..., description="List of memory injections tailored for agents")

async def convert_scenario_to_injections(
    scenario_description: str,
    target_agent_ids: List[uuid.UUID],
    strength: float = 1.0,
    context_id: Optional[str] = None
) -> List[MemoryInjection]:
    """
    Converts a high-level scenario description into specific memory injections for target agents.
    If target_agent_ids is empty, it's treated as a global event and handled directly by the simulation runner.
    If target_agent_ids are provided, the LLM crafts tailored memory snippets for those specific actors.
    """
    if not target_agent_ids:
        # A global scenario without specific targets is a raw broadcast
        logger.info("scenario_conversion_skipped_global", context_id=context_id)
        return []
        
    try:
        system_prompt = (
            "You are a simulation game master. Your task is to take a high-level scenario description "
            "and translate it into specific, localized memories or 'news snippets' for targeted agents. "
            "The memory text should reflect how the scenario manifests in the target agent's reality. "
            f"The impact strength of this scenario is {strength} (where 0.1 is subtle and 2.0 is highly disruptive)."
        )
        
        # In a fully fleshed out system, we would inject the agent's name/persona here.
        # For now, we ask the LLM to generate generic but targeted injections based on the UUIDs provided.
        prompt = (
            f"SCENARIO DESCRIPTION: {scenario_description}\n\n"
            f"TARGET AGENT IDs: {[str(aid) for aid in target_agent_ids]}\n\n"
            "Generate one MemoryInjection per target agent."
        )
        
        logger.info(
            "converting_scenario", 
            target_count=len(target_agent_ids), 
            strength=strength, 
            context_id=context_id
        )
        
        result = await complete_structured(
            prompt=prompt,
            response_schema=ScenarioInjectionResult,
            system=system_prompt,
            context_id=context_id
        )
        
        logger.info("scenario_converted", injection_count=len(result.injections), context_id=context_id)
        return result.injections
        
    except Exception as e:
        logger.error("scenario_conversion_failed", error=str(e), context_id=context_id)
        raise SimWorldError(f"Failed to convert scenario to injections: {str(e)}") from e
