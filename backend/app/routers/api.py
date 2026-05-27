from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.routers.routes import analytics, auth, settings, simulate, tickets

public_router = APIRouter(prefix="/api")

public_router.include_router(auth.router, prefix="/auth", tags=["auth"])

protected = [Depends(get_current_user)]
public_router.include_router(
    analytics.router, prefix="/analytics", tags=["analytics"], dependencies=protected
)
public_router.include_router(
    tickets.router, prefix="/tickets", tags=["tickets"], dependencies=protected
)
public_router.include_router(
    simulate.router, prefix="/simulate", tags=["simulate"], dependencies=protected
)
public_router.include_router(
    settings.router, prefix="/settings", tags=["settings"], dependencies=protected
)


@public_router.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
