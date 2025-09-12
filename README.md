# Backend Challenge API

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
    # Main database connection URL for the application
    DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
    
    # Database connection URL specifically for Alembic migrations
    DATABASE_MIGRATION_URL=postgresql+psycopg2://user:password@host:port/database
    
    # Secret key for JWT token encoding and other security purposes
    SECRET_KEY=your-super-secret-key
    
    # URL for the Redis server, used for caching and background tasks
    REDIS_URL=redis://localhost:6379/0
    
    # API key for Brevo (formerly Sendinblue) email service
    BREVO_API_KEY=your-brevo-api-key
    
    # Email address used as the sender for outgoing emails
    SENDER_EMAIL=your-email@example.com
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

## High Level Architecture
<img width="880" height="449" alt="diagram-export-12-9-2025-11_24_10-pm" src="https://github.com/user-attachments/assets/da00f5bf-788f-46fa-a381-3e1aef04e430" />

## Schema Diagram
<img width="3840" height="3613" alt="Untitled diagram _ Mermaid Chart-2025-09-12-173843" src="https://github.com/user-attachments/assets/62d796ba-7319-4564-a105-51ffca3caecc" />

## Deployment

This project is configured for deployment on Render. The `render.yaml` file contains the deployment configuration.
