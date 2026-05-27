from fastapi import APIRouter

from app.dependencies import AnalyticsServiceDep
from app.schemas.analytics import AnalyticsReport

router = APIRouter()


@router.get("", response_model=AnalyticsReport)
async def get_analytics(analytics_service: AnalyticsServiceDep) -> AnalyticsReport:
    return await analytics_service.build_report()
