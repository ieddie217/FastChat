from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ...core.auth import DEMO_USERS, create_access_token
from pydantic import BaseModel, Field
from ...core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=settings.JWT_EXPIRE_MIN * 60)

@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = DEMO_USERS.get(form.username)
    if not user or user["password"] != form.password:
        raise HTTPException(status_code=401, detail="invalid_credentials")
    token = create_access_token(sub=user["username"], roles=user.get("roles", []))
    return TokenResponse(access_token=token)
