import asyncio
import logging
import os
from dotenv import load_dotenv

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.crud import booking as booking_crud
from app.schemas import schemas

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info(f"CELERY WORKER DATABASE_URL: {os.getenv('DATABASE_URL')}")


@celery_app.task(name="process_booking")
def process_booking_task(booking_data: dict, user_id: int):
    """
    Celery task to process a booking request.
    """
    logger.info(f"Received booking request for user {user_id}. Booking data: {booking_data}")
    
    async def run_booking_logic():
        async with AsyncSessionLocal() as db:
            try:
                booking_schema = schemas.BookingCreate(**booking_data)
                await booking_crud.create_booking(
                    db=db, booking=booking_schema, user_id=user_id
                )
                logger.info(f"Successfully processed booking for user {user_id} and event {booking_data.get('event_id')}.")
            except Exception as e:
                logger.exception(f"Booking/waitlist request failed for user {user_id} and event {booking_data.get('event_id')}.")
                raise
    
    asyncio.run(run_booking_logic())