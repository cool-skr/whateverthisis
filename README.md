# Evently API

Backend system for the Evently platform.

## Features

- User authentication and authorization
- Event creation and management
- Ticket booking and cancellation
- Waitlist for full events
- Admin panel for analytics
- Background tasks for booking processing and email notifications

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/evently.git
    cd evently
    ```
2.  Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set up the environment variables:
    Create a `.env` file in the root directory and add the following variables:
    ```
    DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
    SECRET_KEY=your-secret-key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    BREVO_API_KEY=your-brevo-api-key
    SENDER_EMAIL=your-sender-email
    REDIS_URL=redis://localhost:6379/0
    ```

## Database Migrations

This project uses Alembic for database migrations.

To create a new migration:
```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply the migrations:
```bash
alembic upgrade head
```

## Running the Application

To run the application:
```bash
uvicorn app.main:app --reload
```

## Running the Celery Worker

To run the Celery worker for background tasks:
```bash
celery -A app.workers.celery_app worker --loglevel=info
```

## API Endpoints

The API documentation is available at `http://localhost:8000/docs` when the application is running.

### Authentication

- `POST /auth/register`: Register a new user.
- `POST /auth/login`: Login and get an access token.

### Events

- `GET /events`: Get a list of all events.
- `POST /events`: Create a new event.
- `GET /events/{event_id}`: Get details of a specific event.
- `PUT /events/{event_id}`: Update an event.
- `DELETE /events/{event_id}`: Delete an event.

### Bookings

- `POST /bookings`: Request a booking for an event.
- `GET /users/me/bookings`: Get all bookings for the current user.
- `POST /bookings/{booking_id}/cancel`: Cancel a booking.

### Admin

- `GET /admin/analytics`: Get analytics overview.

## Deployment

This project is configured for deployment on Render. The `render.yaml` file contains the deployment configuration.
