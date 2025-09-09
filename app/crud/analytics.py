from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, cast, Float

from app.models import models
from app.schemas import schemas

async def get_analytics_overview(db: AsyncSession) -> schemas.AnalyticsOverview:
    """
    Performs aggregation queries to generate an analytics overview.
    """
    total_bookings_result = await db.execute(
        select(func.count(models.Booking.id))
        .filter(models.Booking.status == models.BookingStatus.CONFIRMED)
    )
    total_confirmed_bookings = total_bookings_result.scalar_one_or_none() or 0

    total_booked_seats_result = await db.execute(
        select(func.sum(models.Event.booked_seats))
        .filter(models.Event.status == models.EventStatus.ACTIVE)
    )
    total_booked_seats = total_booked_seats_result.scalar_one_or_none() or 0

    total_capacity_result = await db.execute(
        select(func.sum(models.Event.capacity))
        .filter(models.Event.status == models.EventStatus.ACTIVE)
    )
    total_capacity = total_capacity_result.scalar_one_or_none() or 1 # Avoid division by zero

    capacity_utilization_percentage = round((total_booked_seats / total_capacity) * 100, 2) if total_capacity > 0 else 0

   
    popular_events_result = await db.execute(
        select(
            models.Event.id.label("event_id"),
            models.Event.name.label("event_name"),
            func.count(models.Booking.id).label("booking_count"),
        )
        .join(models.Booking, models.Event.id == models.Booking.event_id)
        .filter(models.Booking.status == models.BookingStatus.CONFIRMED)
        .group_by(models.Event.id, models.Event.name)
        .order_by(func.count(models.Booking.id).desc())
        .limit(5)
    )
    most_popular_events = popular_events_result.all()
    
    return schemas.AnalyticsOverview(
        total_confirmed_bookings=total_confirmed_bookings,
        capacity_utilization_percentage=capacity_utilization_percentage,
        most_popular_events=most_popular_events,
    )