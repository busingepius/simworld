from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

from core.llm_client import complete_structured
from core.logging import get_logger
from db.neo4j import get_neo4j
from core.exceptions import SimWorldError

logger = get_logger(__name__)

class Entity(BaseModel):
    name: str = Field(..., description="Name of the entity (e.g., person name, organization name, concept)")
    type: str = Field(..., description="Type of the entity (e.g., PERSON, ORGANIZATION, CONCEPT, LOCATION)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs of attributes for this entity")

class Relationship(BaseModel):
    source: str = Field(..., description="Name of the source entity")
    target: str = Field(..., description="Name of the target entity")
    type: str = Field(..., description="Type of the relationship (e.g., WORKS_FOR, KNOWS, BELIEVES_IN)")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Key-value pairs of attributes for this relationship")

class GraphExtraction(BaseModel):
    entities: List[Entity] = Field(default_factory=list, description="List of extracted entities")
    relationships: List[Relationship] = Field(default_factory=list, description="List of extracted relationships between entities")

async def extract_graph_from_text(text: str, context_id: Optional[str] = None) -> GraphExtraction:
    """
    Extracts entities and relationships from raw text using the LLM.
    """
    system_prompt = (
        "You are an expert knowledge graph extractor. "
        "Your task is to analyze the provided text and extract a knowledge graph containing entities and relationships. "
        "Focus on social dynamics, beliefs, affiliations, and organizational structures."
    )
    
    logger.info("extracting_graph_from_text", text_length=len(text), context_id=context_id)
    
    extraction = await complete_structured(
        prompt=text,
        response_schema=GraphExtraction,
        system=system_prompt,
        context_id=context_id
    )
    
    return extraction

async def build_graph_for_world(world_id: uuid.UUID, org_id: uuid.UUID, text: str, context_id: Optional[str] = None) -> None:
    """
    Extracts a graph from seed material text and loads it into Neo4j, scoped to a specific world.
    """
    try:
        # 1. Extract graph data via LLM
        extraction = await extract_graph_from_text(text, context_id=context_id)
        
        if not extraction.entities:
            logger.warning("graph_builder_no_entities_extracted", world_id=str(world_id), context_id=context_id)
            return

        # 2. Write to Neo4j
        neo4j_client = get_neo4j()
        driver = neo4j_client.get_driver()
        
        async with driver.session() as session:
            # We use a transaction function to ensure atomicity
            await session.execute_write(_merge_graph_tx, str(world_id), str(org_id), extraction)
            
        logger.info(
            "graph_built_successfully", 
            world_id=str(world_id), 
            entities_count=len(extraction.entities), 
            relationships_count=len(extraction.relationships),
            context_id=context_id
        )
        
    except Exception as e:
        logger.error("graph_build_failed", error=str(e), world_id=str(world_id), context_id=context_id)
        raise SimWorldError(f"Failed to build graph: {str(e)}", detail={"world_id": str(world_id)}) from e

async def _merge_graph_tx(tx, world_id: str, org_id: str, extraction: GraphExtraction):
    """
    Neo4j transaction function to merge entities and relationships.
    All nodes are labeled with 'Entity' and their specific type, and scoped by world_id and org_id.
    """
    # 1. Merge entities
    for entity in extraction.entities:
        # Clean up labels to be safe for Neo4j (alphanumeric only)
        safe_type = "".join(c for c in entity.type if c.isalnum()) or "Unknown"
        
        query = f"""
        MERGE (n:Entity:{safe_type} {{name: $name, world_id: $world_id, org_id: $org_id}})
        SET n += $attributes
        """
        await tx.run(
            query,
            name=entity.name,
            world_id=world_id,
            org_id=org_id,
            attributes=entity.attributes
        )
        
    # 2. Merge relationships
    for rel in extraction.relationships:
        safe_rel_type = "".join(c for c in rel.type.upper() if c.isalnum() or c == "_") or "RELATED_TO"
        
        query = f"""
        MATCH (source:Entity {{name: $source_name, world_id: $world_id, org_id: $org_id}})
        MATCH (target:Entity {{name: $target_name, world_id: $world_id, org_id: $org_id}})
        MERGE (source)-[r:{safe_rel_type}]->(target)
        SET r += $attributes
        """
        await tx.run(
            query,
            source_name=rel.source,
            target_name=rel.target,
            world_id=world_id,
            org_id=org_id,
            attributes=rel.attributes
        )
