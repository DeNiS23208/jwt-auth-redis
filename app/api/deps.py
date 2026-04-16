from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis import get_value, access_key, blacklist_key

from app.core.security import decode_token
from app.db.models.user import User
from app.db.session import AsyncSessionLocal


security = HTTPBearer()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный токен"
        )

    jti = payload.get("jti")
    user_id = payload.get("sub")
    token_type = payload.get("type")

    if jti is None or user_id is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный payload токена"
        )

    # Проверяем, не находится ли токен в черном списке
    is_blacklisted = await get_value(blacklist_key(jti))
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен заблокирован"
        )

    # Проверяем, находится ли токен в белом списке
    is_whitelisted = await get_value(access_key(jti))
    if not is_whitelisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не найден в белом списке",
        )

    # Получаем пользователя из базы данных
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )

    return user
