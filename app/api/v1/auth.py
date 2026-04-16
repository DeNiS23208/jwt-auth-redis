from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import register_user, login_user
from app.services.auth_service import refresh_access_token
from pydantic import BaseModel
from app.core.redis import delete_value, blacklist_key, access_key, set_value
from app.core.security import decode_token

security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, data)
        return UserResponse(
            id=user.id, email=user.email, is_active=user.is_active, role_id=user.role_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        tokens = await login_user(db, data)
        return TokenResponse(**tokens)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error))


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh(data: RefreshTokenRequest):
    try:
        return await refresh_access_token(data.refresh_token)
    except ValueError as Error:
        raise HTTPException(status_code=401, detail=str(Error))
    
    
    

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный токен")
    
    jti = payload.get("jti")
    
    if not jti:
        raise HTTPException(status_code=401, detail="Неверный токен")
    
    # Удаляем токен из белого списка и добавляем в черный список
    await delete_value(access_key(jti))
    await set_value(blacklist_key(jti), "1")
    return {"message": "Успешный выход из системы"}
