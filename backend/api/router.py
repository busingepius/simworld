from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from api.routes import (
    auth,
    worlds,
    seed,
    agents,
    simulations,
    scenarios,
    reports,
    calibrations,
)
from core.exceptions import (
    SimWorldError,
    WorldNotFoundError,
    SimulationLimitExceededError,
    LLMCallFailedError,
    OrganisationNotFoundError,
    AuthenticationError
)

api_router = APIRouter()

# Mount all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(worlds.router, prefix="/worlds", tags=["worlds"])
api_router.include_router(seed.router, prefix="/worlds", tags=["seed_materials"])
api_router.include_router(agents.router, prefix="/worlds", tags=["agents"])
api_router.include_router(simulations.router, prefix="/worlds", tags=["simulations"])
api_router.include_router(scenarios.router, prefix="/worlds", tags=["scenarios"])
api_router.include_router(reports.router, prefix="/worlds", tags=["reports"])
api_router.include_router(calibrations.router, prefix="/worlds", tags=["calibrations"])

def setup_exception_handlers(app):
    """
    Registers global exception handlers for the FastAPI app to map typed 
    core exceptions to standard HTTP JSON responses.
    """
    
    @app.exception_handler(WorldNotFoundError)
    async def world_not_found_handler(request: Request, exc: WorldNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"code": "WORLD_NOT_FOUND", "message": exc.message, "detail": exc.detail}}
        )

    @app.exception_handler(OrganisationNotFoundError)
    async def org_not_found_handler(request: Request, exc: OrganisationNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"code": "ORGANISATION_NOT_FOUND", "message": exc.message, "detail": exc.detail}}
        )

    @app.exception_handler(SimulationLimitExceededError)
    async def simulation_limit_handler(request: Request, exc: SimulationLimitExceededError):
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"error": {"code": "SIMULATION_LIMIT_EXCEEDED", "message": exc.message, "detail": exc.detail}}
        )

    @app.exception_handler(LLMCallFailedError)
    async def llm_failed_handler(request: Request, exc: LLMCallFailedError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": {"code": "LLM_CALL_FAILED", "message": exc.message, "detail": exc.detail}}
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": {"code": "UNAUTHORIZED", "message": exc.message, "detail": exc.detail}}
        )

    @app.exception_handler(SimWorldError)
    async def fallback_simworld_error_handler(request: Request, exc: SimWorldError):
        # Fallback for any other custom exceptions
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"code": "BAD_REQUEST", "message": exc.message, "detail": exc.detail}}
        )
