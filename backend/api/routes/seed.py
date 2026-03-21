import uuid
import os
import shutil
from fastapi import APIRouter, Depends, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_org, get_db
from models.organisation import Organisation
from core.config import get_settings
from core.llm_client import complete
from workers.celery_app import celery
from core.exceptions import WorldNotFoundError
from core import crud

settings = get_settings()
router = APIRouter()


class GenerateSeedRequest(BaseModel):
    prompt: str

@router.post("/{world_id}/seed")
async def upload_seed_material(
    world_id: uuid.UUID,
    file: UploadFile = File(...),
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})

    # Save file locally for MVP
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    file_path = os.path.join(settings.STORAGE_PATH, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    material = await crud.create_seed_material(
        db,
        org_id=org.id,
        world_id=world_id,
        filename=file.filename,
        file_type=file.content_type or "application/octet-stream",
        storage_path=file_path
    )
    
    # Dispatch task
    celery.send_task("workers.ingest.ingest_seed_material", args=[str(material.id)])

    return {"status": "accepted", "material_id": material.id}


@router.post("/{world_id}/seed/generate")
async def generate_seed_material(
    world_id: uuid.UUID,
    body: GenerateSeedRequest,
    org: Organisation = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    world = await crud.get_world(db, world_id, org.id)
    if not world:
        raise WorldNotFoundError(detail={"world_id": str(world_id)})

    system = (
        "You are a world-building assistant. Given a short description, "
        "generate rich, detailed seed material for a social simulation. "
        "Include characters with names, roles, and personalities; key locations; "
        "ongoing conflicts or tensions; and any rules or norms that govern the world. "
        "Write in clear prose — no markdown headers, just well-structured paragraphs."
    )

    content = await complete(prompt=body.prompt, system=system, max_tokens=1500, temperature=0.8)

    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    filename = f"generated_{uuid.uuid4().hex[:8]}.txt"
    file_path = os.path.join(settings.STORAGE_PATH, filename)

    with open(file_path, "w") as f:
        f.write(content)

    material = await crud.create_seed_material(
        db,
        org_id=org.id,
        world_id=world_id,
        filename=filename,
        file_type="text/plain",
        storage_path=file_path
    )

    celery.send_task("workers.ingest.ingest_seed_material", args=[str(material.id)])

    return {"status": "accepted", "material_id": material.id, "preview": content}
