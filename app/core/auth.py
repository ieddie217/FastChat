import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Demo users (replace with DB + hashed passwords)
DEMO_USERS: Dict[str, Dict] = {
    "demo": {"username": "demo", "password": "demo123", "roles": ["user"]}
}

def create_access_token(sub: str, roles: Optional[List[str]] = None, minutes: int = settings.JWT_EXPIRE_MIN) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "roles": roles or [],
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            leeway=15,                 # <— allow 15s skew
            options={"require": ["exp","iat"]},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token_expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid_token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    claims = verify_token(token)
    return {"username": claims["sub"], "roles": claims.get("roles", [])}
