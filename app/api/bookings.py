from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.schemas import schemas
from app.models import models
from app.crud import booking as booking_crud
from app.api.dependencies import get_current_user

router = APIRouter(tags=["Bookings"])

@router.post("/bookings", response_model=schemas.Booking, status_code=status.HTTP_201_CREATED)
async def create_a_booking(
    booking: schemas.BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Create a new booking for the currently authenticated user.
    """

    return await booking_crud.create_booking(db=db, booking=booking, user_id=current_user.id)

@router.get("/users/me/bookings", response_model=List[schemas.Booking])
async def read_user_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Retrieve all bookings for the currently authenticated user.
    """
    return await booking_crud.get_bookings_by_user(db=db, user_id=current_user.id)

@router.post("/bookings/{booking_id}/cancel", response_model=schemas.Booking)
async def cancel_a_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Cancel a booking. A user can only cancel their own bookings.
    """

    result = await db.execute(
        select(models.Booking)
        .options(selectinload(models.Booking.event))
        .filter(models.Booking.id == booking_id)
    )
    booking_to_cancel = result.scalars().first()
    
    if not booking_to_cancel:
        raise HTTPException(status_code=404, detail="Booking not found")

   
    if booking_to_cancel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this booking",
        )

    return await booking_crud.cancel_booking(db=db, booking=booking_to_cancel)