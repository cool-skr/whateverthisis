from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import schemas
from app.models import models
from app.crud import analytics as analytics_crud
from app.api.dependencies import get_current_admin_user

router = APIRouter(tags=["Admin"])

@router.get("/analytics/overview", response_model=schemas.AnalyticsOverview)
async def get_system_analytics(
    db: AsyncSession = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """
    Retrieve system-wide analytics. Only accessible by admin users.
    """
    return await analytics_crud.get_analytics_overview(db=db)