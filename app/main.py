from fastapi import FastAPI
from app.api import auth, events, bookings, admin 

app = FastAPI(
    title="Evently API",
    description="Backend system for the Evently platform.",
    version="0.1.0",
)

# Routers
app.include_router(auth.router, prefix="/auth")
app.include_router(events.router)
app.include_router(bookings.router)
app.include_router(admin.router, prefix="/admin") 
@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Root endpoint for health check.
    """
    return {"status": "ok", "message": "Welcome to Evently API"}