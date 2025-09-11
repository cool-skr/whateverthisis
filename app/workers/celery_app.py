from celery import Celery
import os
from dotenv import load_dotenv
import ssl

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    broker_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_REQUIRED
    },
    redis_backend_use_ssl = {
        'ssl_cert_reqs': ssl.CERT_REQUIRED
    }
)
