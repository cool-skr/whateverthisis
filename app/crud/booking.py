from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models import models
from app.schemas import schemas
from typing import List
from sqlalchemy.orm import selectinload

async def create_booking(
    db: AsyncSession, booking: schemas.BookingCreate, user_id: int
) -> models.Booking:
    """
    Creates a booking for a user, ensuring event capacity is not exceeded.
    Uses SELECT FOR UPDATE to lock the event row during the transaction.
    """
    
    result = await db.execute(
        select(models.Event)
        .filter(models.Event.id == booking.event_id)
        .with_for_update()
    )
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    available_seats = event.capacity - event.booked_seats
    if available_seats < booking.tickets_booked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Not enough available seats. Only {available_seats} left.",
        )

    db_booking = models.Booking(
        user_id=user_id,
        event_id=booking.event_id,
        tickets_booked=booking.tickets_booked,
    )
    db.add(db_booking)

    event.booked_seats += booking.tickets_booked
    
    await db.commit()
    
    result = await db.execute(
        select(models.Booking)
        .options(selectinload(models.Booking.event)) 
        .filter(models.Booking.id == db_booking.id)
    )
    
    final_booking = result.scalars().first()
    return final_booking 

async def get_bookings_by_user(db: AsyncSession, user_id: int) -> List[models.Booking]:
    """
    Retrieves all bookings for a specific user, with event details eagerly loaded.
    """
    result = await db.execute(
        select(models.Booking)
        .options(selectinload(models.Booking.event))
        .filter(models.Booking.user_id == user_id)
        .order_by(models.Booking.booked_at.desc())
    )
    return result.scalars().all()

async def get_booking(db: AsyncSession, booking_id: int) -> models.Booking | None:
    """
    Retrieves a single booking by its ID.
    """
    result = await db.execute(
        select(models.Booking).filter(models.Booking.id == booking_id)
    )
    return result.scalars().first()




async def cancel_booking(db: AsyncSession, booking: models.Booking) -> models.Booking:
    """
    Cancels a booking and decrements the event's booked_seats counter.
    This function assumes the booking object is passed with its event relationship loaded.
    """

    result = await db.execute(
        select(models.Event)
        .filter(models.Event.id == booking.event_id)
        .with_for_update()
    )
    event = result.scalars().first()

    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated event for this booking could not be found."
        )

    if booking.status == models.BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Booking is already cancelled"
        )
    
    event.booked_seats -= booking.tickets_booked
    booking.status = models.BookingStatus.CANCELLED

    
    await db.commit()
    
    
    await db.refresh(booking)
    await db.refresh(event)  

    return booking