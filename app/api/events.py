from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.db.session import get_db
from app.schemas import schemas
from app.models import models
from app.crud import event as event_crud
from app.api.dependencies import get_current_admin_user

router = APIRouter(tags=["Events"])

@router.post("/events", response_model=schemas.Event, status_code=status.HTTP_201_CREATED)
async def create_new_event(
    event: schemas.EventCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """
    Create a new event. This endpoint is protected and only accessible by admin users.
    """
    return await event_crud.create_event(db=db, event=event, creator_id=admin_user.id)

@router.get("/events", response_model=List[schemas.Event])
async def read_events(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of all upcoming events. This is a public endpoint.
    """
    events = await event_crud.get_events(db, skip=skip, limit=limit)
    return events

@router.get("/events/{event_id}", response_model=schemas.Event)
async def read_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve details for a single event. This is a public endpoint.
    """
    db_event = await event_crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event

@router.put("/events/{event_id}", response_model=schemas.Event)
async def update_event(
    event_id: int,
    event_in: schemas.EventCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """
    Update an event's details. This is a protected endpoint for admin users.
    """
    event_to_update = await event_crud.get_event(db, event_id=event_id)
    if not event_to_update:
        raise HTTPException(status_code=404, detail="Event not found")

    if event_to_update.created_by != admin_user.id:
        # Allow any admin to update
        pass

    updated_event = await event_crud.update_event(
        db=db, event_to_update=event_to_update, event_in=event_in
    )
    return updated_event

@router.post("/events/{event_id}/cancel", response_model=schemas.Event)
async def cancel_an_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    admin_user: models.User = Depends(get_current_admin_user),
):
    """
    Cancel an event. This will also cancel all confirmed bookings for the event.
    Only accessible by admin users.
    """
    result = await db.execute(
        select(models.Event)
        .options(selectinload(models.Event.bookings))
        .filter(models.Event.id == event_id)
    )
    event_to_cancel = result.scalars().first()
    
    if not event_to_cancel:
        raise HTTPException(status_code=404, detail="Event not found")
        
    return await event_crud.cancel_event(db=db, event_to_cancel=event_to_cancel)