import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from core.llm_client import complete_structured
from core.logging import get_logger
from core.exceptions import SimWorldError
from models.simulation_state import SimulationState

logger = get_logger(__name__)

class ReportSection(BaseModel):
    title: str = Field(..., description="Title of the report section")
    content: str = Field(..., description="Detailed content and analysis for this section")

class GeneratedReport(BaseModel):
    summary: str = Field(..., description="A high-level executive summary of the simulation outcome")
    sections: List[ReportSection] = Field(..., description="Detailed analytical sections")
    confidence_score: float = Field(..., description="Confidence score of the prediction/analysis from 0.0 to 1.0")

async def generate_report_from_state(
    run_id: uuid.UUID,
    world_id: uuid.UUID,
    state: SimulationState,
    context_id: Optional[str] = None
) -> GeneratedReport:
    """
    Analyzes a completed simulation state and produces a structured prediction report.
    """
    logger.info("generating_report", run_id=str(run_id), world_id=str(world_id), context_id=context_id)
    
    try:
        # Construct the context for the LLM to analyze
        # In a full implementation, we might also query Neo4j here to pull historical context.
        # For now, the SimulationState provides the core data.
        
        state_context = f"""
        OPINION DISTRIBUTIONS:
        {state.opinion_distributions}
        
        COALITIONS:
        {state.coalitions}
        
        TRENDING TOPICS:
        {state.trending_topics}
        """
        
        system_prompt = (
            "You are an expert geopolitical and social dynamics analyst. "
            "Your task is to review the data from a multi-agent simulation and generate a comprehensive, "
            "structured prediction report. Your analysis must cover the prevailing opinions, "
            "emerging coalitions, and potential future trajectories based on the simulation state."
        )
        
        prompt = (
            "Analyze the following simulation state and generate an executive report.\n\n"
            f"SIMULATION STATE:\n{state_context}\n\n"
            "Ensure the report has a clear executive summary and logical sections (e.g., 'Key Findings', "
            "'Coalition Shifts', 'Risk Assessment')."
        )
        
        report = await complete_structured(
            prompt=prompt,
            response_schema=GeneratedReport,
            system=system_prompt,
            context_id=context_id
        )
        
        logger.info(
            "report_generated", 
            run_id=str(run_id), 
            world_id=str(world_id), 
            confidence=report.confidence_score,
            sections_count=len(report.sections),
            context_id=context_id
        )
        
        return report

    except Exception as e:
        logger.error("report_generation_failed", run_id=str(run_id), error=str(e), context_id=context_id)
        raise SimWorldError(f"Failed to generate report: {str(e)}", detail={"run_id": str(run_id)}) from e
