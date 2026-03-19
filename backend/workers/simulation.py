import asyncio
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from workers.celery_app import celery
from core.logging import get_logger
from core.simulation import run_simulation
from core.scenario import convert_scenario_to_injections
from db.session import AsyncSessionFactory
from models.simulation_run import SimulationRun
from models.agent_persona import AgentPersona
from models.scenario import Scenario
from models.simulation_state import SimulationState

logger = get_logger(__name__)

async def _process_simulation(run_id_str: str):
    run_id = uuid.UUID(run_id_str)
    
    async with AsyncSessionFactory() as session:
        try:
            # 1. Fetch simulation run
            run = await session.get(SimulationRun, run_id)
            if not run:
                raise ValueError(f"SimulationRun {run_id_str} not found.")

            # Update status to running
            run.status = "running"
            await session.commit()

            # 2. Fetch active agents for this world
            result = await session.execute(
                select(AgentPersona).where(
                    AgentPersona.world_id == run.world_id,
                    AgentPersona.is_active == True
                )
            )
            agents = list(result.scalars().all())
            
            if not agents:
                raise ValueError(f"No active agents found in world {run.world_id}")

            # 3. Handle Scenario if linked
            scenario_injection_text = None
            if run.scenario_id:
                scenario = await session.get(Scenario, run.scenario_id)
                if scenario:
                    scenario_injection_text = scenario.description
                    # If specific targets were specified, we would fetch injections here and apply them to agent memory
                    # For MVP, passing description as global injection
            
            # 4. Run OASIS wrapper
            final_state = await run_simulation(
                run_id=run.id,
                world_id=run.world_id,
                org_id=run.org_id,
                agents=agents,
                rounds=run.rounds,
                scenario_injection=scenario_injection_text,
                context_id=str(run.id)
            )

            # 5. Persist simulation state
            db_state = SimulationState(
                org_id=run.org_id,
                world_id=run.world_id,
                run_id=run.id,
                opinion_distributions=final_state.opinion_distributions,
                coalitions=final_state.coalitions,
                trending_topics=final_state.trending_topics,
                raw_log_path=f"local/logs/{run_id_str}.txt"
            )
            session.add(db_state)
            
            # Update run to complete
            run.status = "complete"
            await session.commit()
            
            # Dispatch report generation task
            celery.send_task("workers.report.generate_run_report", args=[str(run.id), str(db_state.id)])

        except Exception as e:
            await session.rollback()
            # Try to mark run as failed
            run_failed = await session.get(SimulationRun, run_id)
            if run_failed:
                run_failed.status = "failed"
                await session.commit()
            raise

@celery.task(bind=True, max_retries=1, default_retry_delay=300)
def run_simulation_task(self, run_id: str):
    """
    Celery task to execute a multi-agent simulation run in the background.
    """
    try:
        asyncio.run(_process_simulation(run_id))
    except Exception as exc:
        logger.error("celery_task_failed", task="run_simulation_task", run_id=run_id, error=str(exc))
        raise self.retry(exc=exc)
