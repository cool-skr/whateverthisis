from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import models
from app.schemas import schemas
from app.services.security import hash_password

async def get_user_by_email(db: AsyncSession, email: str) -> models.User | None:
    result = await db.execute(select(models.User).filter(models.User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: schemas.UserCreate) -> models.User:
    hashed_pass = hash_password(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pass
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user