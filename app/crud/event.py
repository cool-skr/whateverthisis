from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import models
from app.schemas import schemas

async def create_event(db: AsyncSession, event: schemas.EventCreate, creator_id: int) -> models.Event:
    db_event = models.Event(**event.model_dump(), created_by=creator_id)
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_event(db: AsyncSession, event_id: int) -> models.Event | None:
    result = await db.execute(select(models.Event).filter(models.Event.id == event_id))
    return result.scalars().first()

async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Event]:
    result = await db.execute(
        select(models.Event)
        .filter(models.Event.status == models.EventStatus.ACTIVE) 
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_event_with_bookings(db: AsyncSession, event_id: int) -> models.Event | None:
    """
    Retrieves an event by its ID, eagerly loading its bookings.
    """
    result = await db.execute(
        select(models.Event)
        .options(selectinload(models.Event.bookings))
        .filter(models.Event.id == event_id)
    )
    return result.scalars().first()

async def update_event(
    db: AsyncSession, event_to_update: models.Event, event_in: schemas.EventCreate
) -> models.Event:
    """
    Updates an event's details in the database.
    """
    
    update_data = event_in.model_dump(exclude_unset=True)
    
    
    for key, value in update_data.items():
        setattr(event_to_update, key, value)
        
    db.add(event_to_update)
    await db.commit()
    await db.refresh(event_to_update)
    return event_to_update

async def delete_event(db: AsyncSession, event_to_delete: models.Event):
    """
    Deletes an event from the database.
    """
    await db.delete(event_to_delete)
    await db.commit()

async def cancel_event(db: AsyncSession, event_to_cancel: models.Event) -> models.Event:
    """
    Cancels an event and all of its confirmed bookings.
    Assumes the event object is passed with its bookings relationship eagerly loaded.
    """
    
    event_to_cancel.status = models.EventStatus.CANCELLED
    
    # Cancel all associated confirmed bookings
    for booking in event_to_cancel.bookings:
        if booking.status == models.BookingStatus.CONFIRMED:
            booking.status = models.BookingStatus.CANCELLED
            
    await db.commit()
    await db.refresh(event_to_cancel)
    return event_to_cancel