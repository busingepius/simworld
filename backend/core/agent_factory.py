import uuid
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from core.llm_client import complete_structured
from core.logging import get_logger
from core.exceptions import SimWorldError
from db.neo4j import get_neo4j

logger = get_logger(__name__)

class AgentStance(BaseModel):
    topic: str = Field(..., description="The specific topic or concept")
    sentiment: float = Field(..., description="Sentiment from -1.0 (strongly opposed) to 1.0 (strongly supportive)")
    reasoning: str = Field(..., description="Internal rationale for this stance")

class AgentPersonality(BaseModel):
    openness: float = Field(..., description="0.0 (conservative/rigid) to 1.0 (inventive/curious)")
    conscientiousness: float = Field(..., description="0.0 (easy-going/careless) to 1.0 (efficient/organized)")
    extraversion: float = Field(..., description="0.0 (solitary/reserved) to 1.0 (outgoing/energetic)")
    agreeableness: float = Field(..., description="0.0 (challenging/detached) to 1.0 (friendly/compassionate)")
    neuroticism: float = Field(..., description="0.0 (secure/confident) to 1.0 (sensitive/nervous)")
    background_story: str = Field(..., description="A short paragraph describing their background and motivations")

class AgentPersonaProfile(BaseModel):
    name: str = Field(..., description="The full name of the agent")
    personality: AgentPersonality = Field(..., description="Psychological traits and background")
    stances: List[AgentStance] = Field(..., description="Key opinions and stances on worldly topics")
    influence_score: float = Field(..., description="Social influence or reach from 0.0 to 1.0")

class AgentFactoryResult(BaseModel):
    personas: List[AgentPersonaProfile] = Field(..., description="Generated personas")

async def generate_personas_from_graph(world_id: uuid.UUID, org_id: uuid.UUID, count: int = 5, context_id: Optional[str] = None) -> List[AgentPersonaProfile]:
    """
    Reads the knowledge graph for a specific world and generates rich Agent personas.
    """
    try:
        # 1. Fetch graph context from Neo4j
        graph_summary = await _fetch_graph_summary(str(world_id), str(org_id))
        
        if not graph_summary.strip():
            logger.warning("agent_factory_empty_graph", world_id=str(world_id))
            graph_summary = "No specific worldly context available. Generate diverse generic personas."

        # 2. Instruct LLM to create personas based on the graph
        system_prompt = (
            "You are a sophisticated behavioral simulation architect. "
            "Your task is to populate a simulation world with rich, believable agent personas. "
            "Use the provided knowledge graph summary to ground the agents in the reality of their world. "
            "Ensure the agents have varied, realistic psychological profiles and conflicting or aligned stances "
            "based on the world's factions and concepts."
        )
        
        prompt = (
            f"Generate exactly {count} distinct agent personas.\n\n"
            f"WORLD KNOWLEDGE GRAPH SUMMARY:\n{graph_summary}\n\n"
            "Ensure their stances reference specific concepts or organizations from the summary if possible."
        )
        
        logger.info("generating_personas", world_id=str(world_id), count=count, context_id=context_id)
        
        result = await complete_structured(
            prompt=prompt,
            response_schema=AgentFactoryResult,
            system=system_prompt,
            context_id=context_id
        )
        
        # Ensure we don't accidentally return more or fewer than requested if LLM drifted slightly
        personas = result.personas[:count]
        
        logger.info("personas_generated", world_id=str(world_id), generated_count=len(personas), context_id=context_id)
        return personas
        
    except Exception as e:
        logger.error("persona_generation_failed", error=str(e), world_id=str(world_id), context_id=context_id)
        raise SimWorldError(f"Failed to generate agent personas: {str(e)}", detail={"world_id": str(world_id)}) from e

async def _fetch_graph_summary(world_id: str, org_id: str) -> str:
    """
    Helper function to query Neo4j and return a textual summary of the world's entities and relationships.
    """
    neo4j_client = get_neo4j()
    
    # Check if driver is initialized, safely return empty if not (for testing/mocking resilience)
    try:
        driver = neo4j_client.get_driver()
    except RuntimeError:
        return ""
        
    async with driver.session() as session:
        # Fetch entities
        entity_query = """
        MATCH (n:Entity {world_id: $world_id, org_id: $org_id})
        RETURN labels(n) as labels, n.name as name
        LIMIT 50
        """
        entity_result = await session.run(entity_query, world_id=world_id, org_id=org_id)
        entities = [f"{record['name']} ({', '.join([l for l in record['labels'] if l != 'Entity'])})" async for record in entity_result]
        
        # Fetch relationships
        rel_query = """
        MATCH (a:Entity {world_id: $world_id, org_id: $org_id})-[r]->(b:Entity {world_id: $world_id, org_id: $org_id})
        RETURN a.name as source, type(r) as type, b.name as target
        LIMIT 50
        """
        rel_result = await session.run(rel_query, world_id=world_id, org_id=org_id)
        relationships = [f"{record['source']} -[{record['type']}]-> {record['target']}" async for record in rel_result]
        
        summary = ""
        if entities:
            summary += "ENTITIES:\n- " + "\n- ".join(entities) + "\n\n"
        if relationships:
            summary += "RELATIONSHIPS:\n- " + "\n- ".join(relationships)
            
        return summary
