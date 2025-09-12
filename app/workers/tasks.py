import asyncio
import logging
import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from app.workers.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.crud import booking as booking_crud
from app.schemas import schemas

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info(f"CELERY WORKER DATABASE_URL: {os.getenv('DATABASE_URL')}")


brevo_configuration = sib_api_v3_sdk.Configuration()
brevo_configuration.api_key['api-key'] = os.getenv('BREVO_API_KEY')
brevo_api_client = sib_api_v3_sdk.ApiClient(brevo_configuration)
brevo_emails_api = sib_api_v3_sdk.TransactionalEmailsApi(brevo_api_client)

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

@celery_app.task(name="send_waitlist_success_email")
def send_waitlist_success_email(user_email: str, user_name: str, event_name: str):
    """
    Sends a confirmation email using the pre-configured Brevo client to a user 
    who got a ticket from the waitlist.
    """
    subject = f"Good news! Tickets are available for {event_name}"
    html_content = f"""
    <p>Hi {user_name},</p>
    <p>A spot has opened up for the event: <strong>{event_name}</strong>!</p>
    <p>We have automatically created a booking for you. You can view it in your booking history.</p>
    <p>Thank you,</p>
    <p>The Evently Team</p>
    """
    sender = {"name": "Evently", "email": os.getenv("SENDER_EMAIL")}
    to = [{"email": user_email, "name": user_name}]
    
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = brevo_emails_api.send_transac_email(send_smtp_email)
        logger.info(f"Waitlist success email sent to {user_email} via Brevo. Response: {api_response.message_id}")
    except ApiException as e:
        logger.exception(f"Failed to send waitlist success email to {user_email} via Brevo: {e}")
        raise
