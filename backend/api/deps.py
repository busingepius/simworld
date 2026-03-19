import uuid
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from db.session import get_db
from models.organisation import Organisation
from core.exceptions import AuthenticationError

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_org(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Organisation:
    """
    Validates the JWT token and returns the authenticated Organisation.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": "UNAUTHORIZED", "message": "Could not validate credentials", "detail": {}}},
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        org_id_str: str = payload.get("sub")
        if org_id_str is None:
            raise credentials_exception
        token_data = uuid.UUID(org_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    org = await db.get(Organisation, token_data)
    if org is None or not org.is_active:
        raise credentials_exception
        
    return org
