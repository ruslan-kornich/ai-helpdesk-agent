from fastapi import APIRouter

from app.routers.routes import settings, simulate, tickets

public_router = APIRouter(prefix="/api")
public_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
public_router.include_router(simulate.router, prefix="/simulate", tags=["simulate"])
public_router.include_router(settings.router, prefix="/settings", tags=["settings"])


@public_router.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
