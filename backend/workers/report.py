import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from workers.celery_app import celery
from core.logging import get_logger
from core.report_agent import generate_report_from_state
from db.session import AsyncSessionFactory
from models.simulation_state import SimulationState
from models.report import Report

logger = get_logger(__name__)

async def _process_report(run_id_str: str, state_id_str: str):
    run_id = uuid.UUID(run_id_str)
    state_id = uuid.UUID(state_id_str)
    
    async with AsyncSessionFactory() as session:
        try:
            # 1. Fetch simulation state
            state = await session.get(SimulationState, state_id)
            if not state:
                raise ValueError(f"SimulationState {state_id_str} not found.")

            # 2. Generate report using LLM analyst
            generated_report = await generate_report_from_state(
                run_id=run_id,
                world_id=state.world_id,
                state=state,
                context_id=run_id_str
            )

            # 3. Persist report to PostgreSQL
            db_report = Report(
                org_id=state.org_id,
                world_id=state.world_id,
                run_id=run_id,
                summary=generated_report.summary,
                sections=[section.model_dump() for section in generated_report.sections],
                confidence_score=generated_report.confidence_score
            )
            session.add(db_report)
            await session.commit()
            
            logger.info("report_persisted", run_id=run_id_str, report_id=str(db_report.id))

        except Exception as e:
            await session.rollback()
            raise

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_run_report(self, run_id: str, state_id: str):
    """
    Celery task to generate an executive report following a simulation run.
    """
    try:
        asyncio.run(_process_report(run_id, state_id))
    except Exception as exc:
        logger.error("celery_task_failed", task="generate_run_report", run_id=run_id, state_id=state_id, error=str(exc))
        raise self.retry(exc=exc)
