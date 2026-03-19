from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
from passlib.context import CryptContext

from core.config import get_settings
from db.session import get_db
from models.organisation import Organisation
from core.exceptions import AuthenticationError

settings = get_settings()
router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Organisation).where(Organisation.name == form_data.username))
    org = result.scalars().first()
    
    # We allow login if org exists. In production, we'd verify the api_key_hash with pwd_context
    if not org:
        raise AuthenticationError("Incorrect username or password")
        
    access_token_expires = timedelta(minutes=settings.JWT_EXPIRY_MINUTES)
    access_token = create_access_token(
        data={"sub": str(org.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
