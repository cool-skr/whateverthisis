from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import models

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
    
    # First, check if the user is already on the waitlist to prevent duplicate entries.
    existing_entry = await get_waitlist_entry(db, event_id=event_id, user_id=user_id)
    if existing_entry:
        return existing_entry # User is already pending, so just return the existing entry.

    # If not, create and add the new waitlist entry.
    db_waitlist_entry = models.WaitlistEntry(
        user_id=user_id,
        event_id=event_id,
        tickets_requested=tickets_requested,
    )
    db.add(db_waitlist_entry)
    await db.commit()
    await db.refresh(db_waitlist_entry)
    return db_waitlist_entry
