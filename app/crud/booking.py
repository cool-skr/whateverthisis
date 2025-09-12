from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models import models
from app.schemas import schemas
from typing import List, Union
from sqlalchemy.orm import selectinload
from app.crud import waitlist as waitlist_crud

async def create_booking(
    db: AsyncSession, booking: schemas.BookingCreate, user_id: int
) -> Union[models.Booking, models.WaitlistEntry]:
    """
    Creates a booking for a user. If the event is full, adds the user to the waitlist.
    Returns either the new Booking object or the new WaitlistEntry object.
    """
    result = await db.execute(
        select(models.Event)
        .filter(models.Event.id == booking.event_id)
        .with_for_update()
    )
    event = result.scalars().first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.status == models.EventStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Cannot book tickets for a cancelled event.")

    available_seats = event.capacity - event.booked_seats
    if available_seats < booking.tickets_booked:
        waitlist_entry = await waitlist_crud.add_to_waitlist(
            db=db,
            event_id=booking.event_id,
            user_id=user_id,
            tickets_requested=booking.tickets_booked
        )
        return waitlist_entry

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

    event_id_for_waitlist = booking.event_id
    await db.commit()
    
    async with db.begin_nested():
        await waitlist_crud.process_waitlist_for_event(db=db, event_id=event_id_for_waitlist)

    await db.refresh(booking)
    await db.refresh(event)  

    return booking
