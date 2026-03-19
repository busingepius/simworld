import asyncio
import uuid
import os
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from workers.celery_app import celery
from core.logging import get_logger
from core.graph_builder import build_graph_for_world
from db.session import AsyncSessionFactory
from models.seed_material import SeedMaterial

logger = get_logger(__name__)

async def _process_ingest(material_id: str) -> None:
    async with AsyncSessionFactory() as session:
        try:
            # 1. Fetch material record
            material = await session.get(SeedMaterial, uuid.UUID(material_id))
            if not material:
                raise ValueError(f"Seed material {material_id} not found.")

            # 2. Read file (Mocking storage for MVP - assuming local text for now)
            # In production, we'd pull from S3 if STORAGE_BACKEND=s3
            try:
                with open(material.storage_path, "r") as f:
                    text_content = f.read()
            except FileNotFoundError:
                raise ValueError(f"File not found at path {material.storage_path}")

            # 3. Process into Knowledge Graph
            await build_graph_for_world(
                world_id=material.world_id, 
                org_id=material.org_id, 
                text=text_content,
                context_id=material_id
            )

            # 4. Mark success
            material.status = "processed"
            await session.commit()
            
            logger.info("seed_material_ingested", material_id=material_id, world_id=str(material.world_id))

        except Exception as e:
            await session.rollback()
            # Mark failed
            if 'material' in locals() and material:
                material.status = "failed"
                await session.commit()
            logger.error("seed_material_ingest_failed", material_id=material_id, error=str(e))
            raise

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_seed_material(self, material_id: str):
    """
    Celery task to asynchronously process seed material into the knowledge graph.
    """
    try:
        asyncio.run(_process_ingest(material_id))
    except Exception as exc:
        logger.error("celery_task_failed", task="ingest_seed_material", material_id=material_id, error=str(exc))
        raise self.retry(exc=exc)
