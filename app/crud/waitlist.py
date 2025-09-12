from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.workers.celery_app import celery_app # Import celery_app
from app.crud import booking as booking_crud
from app.models import models
from app.schemas import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_waitlist_entry(db: AsyncSession, event_id: int, user_id: int) -> models.WaitlistEntry | None:
    """Checks if a user is already on the waitlist for a specific event."""
    result = await db.execute(
        select(models.WaitlistEntry)
        .filter_by(event_id=event_id, user_id=user_id, status=models.WaitlistStatus.PENDING)
    )
    return result.scalars().first()


async def add_to_waitlist(
    db: AsyncSession, *, event_id: int, user_id: int, tickets_requested: int
) -> models.WaitlistEntry:
    """Adds a user to the waitlist for a specific event."""
    
    existing_entry = await get_waitlist_entry(db, event_id=event_id, user_id=user_id)
    if existing_entry:
        return existing_entry # User is already pending, so just return the existing entry.

    db_waitlist_entry = models.WaitlistEntry(
        user_id=user_id,
        event_id=event_id,
        tickets_requested=tickets_requested,
    )
    db.add(db_waitlist_entry)
    await db.commit()
    await db.refresh(db_waitlist_entry)
    return db_waitlist_entry




async def process_waitlist_for_event(db: AsyncSession, event_id: int):
    """
    Checks the waitlist for an event and processes the next entry if seats are available.
    """
    event_result = await db.execute(select(models.Event).filter(models.Event.id == event_id).with_for_update())
    event = event_result.scalars().first()
    if not event: return
    
    available_seats = event.capacity - event.booked_seats
    if available_seats <= 0: return

    waitlist_entry_result = await db.execute(
        select(models.WaitlistEntry)
        .options(selectinload(models.WaitlistEntry.user))
        .filter_by(event_id=event_id, status=models.WaitlistStatus.PENDING)
        .order_by(models.WaitlistEntry.created_at.asc())
        .limit(1)
    )
    next_in_line = waitlist_entry_result.scalars().first()

    if next_in_line and available_seats >= next_in_line.tickets_requested:
        new_booking_or_entry = await booking_crud.create_booking(
            db=db, 
            booking=schemas.BookingCreate(
                event_id=next_in_line.event_id,
                tickets_booked=next_in_line.tickets_requested
            ), 
            user_id=next_in_line.user_id
        )

        if isinstance(new_booking_or_entry, models.Booking):
            next_in_line.status = models.WaitlistStatus.FULFILLED
            db.add(next_in_line)
            await db.commit()
            
            celery_app.send_task(
                'send_waitlist_success_email',
                args=[
                    next_in_line.user.email,
                    next_in_line.user.full_name,
                    event.name
                ]
            )