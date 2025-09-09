# In app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import models
from app.services import security
from app.crud import user as user_crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> models.User:
    """
    Decodes the access token, retrieves the user by email, and returns the user object.
    Raises credentials exception if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    user = await user_crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_admin_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    """
    Checks if the current user is an admin. Raises a forbidden exception if not.
    """
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have sufficient privileges",
        )
    return current_user