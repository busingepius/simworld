from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router, setup_exception_handlers
from core.config import get_settings
from core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("api_startup")
    yield
    from db.neo4j import get_neo4j
    logger.info("api_shutdown")
    client = get_neo4j()
    await client.close()

app = FastAPI(
    title="SimWorld API",
    description="Backend API for SimWorld platform",
    version="0.1.0",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
setup_exception_handlers(app)

# Include main router
app.include_router(api_router, prefix="/api")
