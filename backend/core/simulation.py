import uuid
import json
import asyncio
from typing import List, Dict, Any, Optional

from core.llm_client import complete
from core.logging import get_logger
from core.exceptions import SimWorldError, SimulationLimitExceededError
from models.agent_persona import AgentPersona

logger = get_logger(__name__)

class SimulationStateOutput:
    """Represents the outcome of a simulation run."""
    def __init__(self, run_id: uuid.UUID, opinion_distributions: Dict[str, Any], coalitions: Dict[str, Any], trending_topics: Dict[str, Any], raw_log: str):
        self.run_id = run_id
        self.opinion_distributions = opinion_distributions
        self.coalitions = coalitions
        self.trending_topics = trending_topics
        self.raw_log = raw_log

async def run_simulation(
    run_id: uuid.UUID,
    world_id: uuid.UUID,
    org_id: uuid.UUID,
    agents: List[AgentPersona],
    rounds: int = 5,
    scenario_injection: Optional[str] = None,
    context_id: Optional[str] = None
) -> SimulationStateOutput:
    """
    Orchestrates a multi-agent simulation run (abstracted OASIS logic).
    
    This function simulates interactions between the provided agents over a given number of rounds,
    optionally injecting a scenario/event into their context, and produces a final state output.
    """
    
    if len(agents) == 0:
        raise SimWorldError("Cannot run simulation with 0 agents.", detail={"run_id": str(run_id)})
        
    if rounds > 100:
        raise SimulationLimitExceededError(f"Requested {rounds} rounds exceeds the maximum of 100.", detail={"run_id": str(run_id)})
        
    logger.info("simulation_started", run_id=str(run_id), world_id=str(world_id), agent_count=len(agents), rounds=rounds, context_id=context_id)
    
    simulation_log = []
    
    # Initialize agent states for the simulation
    # In a full OASIS implementation, these would be stateful CAMEL agents.
    # Here we are building the orchestration wrapper that uses our llm_client directly.
    agent_states = {
        agent.id: {
            "name": agent.name,
            "personality": agent.personality,
            "stances": agent.stance,
            "recent_memories": []
        }
        for agent in agents
    }
    
    if scenario_injection:
        simulation_log.append(f"SCENARIO INJECTED: {scenario_injection}")
        for state in agent_states.values():
            state["recent_memories"].append(f"Global Event: {scenario_injection}")

    try:
        # Run simulation rounds
        for current_round in range(1, rounds + 1):
            logger.info("simulation_round_started", run_id=str(run_id), round=current_round, context_id=context_id)
            round_log = f"--- ROUND {current_round} ---\n"
            
            # Limit concurrency to avoid overwhelming the LLM rate limit.
            semaphore = asyncio.Semaphore(3)

            async def _call_agent(agent: AgentPersona):
                async with semaphore:
                    prompt = _build_agent_prompt(agent, agent_states[agent.id], current_round)
                    system = f"You are {agent.name}. Roleplay your reaction based on your personality and stances. Be concise (1-2 sentences)."
                    return await complete(
                        prompt=prompt,
                        system=system,
                        temperature=0.8,
                        context_id=context_id or str(run_id)
                    )

            responses = await asyncio.gather(*[_call_agent(a) for a in agents], return_exceptions=True)
            
            for agent, response in zip(agents, responses):
                if isinstance(response, Exception):
                    logger.error("agent_reaction_failed", agent_id=str(agent.id), error=str(response), context_id=context_id)
                    reaction = "*remained silent*"
                else:
                    reaction = response.strip()
                    
                agent_states[agent.id]["recent_memories"].append(reaction)
                round_log += f"{agent.name}: {reaction}\n"
                
            simulation_log.append(round_log)
            
        # Post-process the simulation to determine distributions, coalitions, and topics
        # In a production OASIS environment, this would be computed from the graph state
        final_state = await _analyze_simulation_outcome(simulation_log, agents, context_id or str(run_id))
        final_state.run_id = run_id
        
        logger.info("simulation_completed", run_id=str(run_id), rounds_completed=rounds, context_id=context_id)
        return final_state
        
    except Exception as e:
        logger.error("simulation_failed_unexpectedly", run_id=str(run_id), error=str(e), context_id=context_id)
        raise SimWorldError(f"Simulation run failed: {str(e)}", detail={"run_id": str(run_id)}) from e

def _build_agent_prompt(agent: AgentPersona, state: dict, current_round: int) -> str:
    """Builds the prompt for an agent's turn."""
    memories = "\n".join(state["recent_memories"][-3:]) # Last 3 memories
    
    prompt = f"It is Round {current_round}.\n"
    prompt += f"Your Background: {state['personality'].get('background_story', '')}\n"
    prompt += f"Recent Events/Thoughts:\n{memories}\n\n"
    prompt += "What do you say or do next? How do your stances affect your view of the current situation?"
    
    return prompt

async def _analyze_simulation_outcome(simulation_log: List[str], agents: List[AgentPersona], context_id: str) -> SimulationStateOutput:
    """
    Analyzes the raw log using the LLM to extract structured distributions and coalitions.
    """
    raw_log = "\n".join(simulation_log)
    
    system_prompt = (
        "You are an analytical engine reviewing a social simulation log. "
        "Extract the prevailing opinion distributions, emerging coalitions between actors, "
        "and the trending topics discussed. Output as raw JSON with keys: "
        "'opinion_distributions', 'coalitions', 'trending_topics'."
    )
    
    # We ask the LLM to synthesize the unstructured log into the structured state
    try:
        analysis_json = await complete(
            prompt=f"SIMULATION LOG:\n{raw_log}",
            system=system_prompt,
            temperature=0.0,
            context_id=context_id
        )
        
        # Clean potential markdown
        clean_json = analysis_json.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
            
        data = json.loads(clean_json.strip())
        
        return SimulationStateOutput(
            run_id=uuid.uuid4(), # Placeholder, overwritten by caller
            opinion_distributions=data.get("opinion_distributions", {}),
            coalitions=data.get("coalitions", {}),
            trending_topics=data.get("trending_topics", {}),
            raw_log=raw_log
        )
    except Exception as e:
        logger.warning("simulation_analysis_failed_fallback", error=str(e), context_id=context_id)
        # Fallback if parsing fails
        return SimulationStateOutput(
            run_id=uuid.uuid4(),
            opinion_distributions={"error": "Analysis parsing failed"},
            coalitions={},
            trending_topics={"topics": ["Unknown"]},
            raw_log=raw_log
        )
