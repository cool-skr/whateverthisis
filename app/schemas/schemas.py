from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models.models import UserRole, BookingStatus, EventStatus

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

# --- Event Schemas ---
class EventBase(BaseModel):
    name: str
    venue: str
    event_time: datetime
    capacity: int

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    booked_seats: int
    status: EventStatus
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Booking Schemas ---
class BookingBase(BaseModel):
    event_id: int
    tickets_booked: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    status: BookingStatus
    booked_at: datetime
    event: Event 

    class Config:
        from_attributes = True

class PopularEvent(BaseModel):
    event_id: int
    event_name: str
    booking_count: int

    class Config:
        from_attributes = True


class AnalyticsOverview(BaseModel):
    total_confirmed_bookings: int
    capacity_utilization_percentage: float
    most_popular_events: List[PopularEvent]