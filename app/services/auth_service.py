from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, create_access_token
from app.db.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.core.redis import set_value, access_key, refresh_key


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email).options(selectinload(User.role))
    )
    return result.scalars().first()


async def register_user(session: AsyncSession, data: RegisterRequest) -> User:
    existing_user = await get_user_by_email(session, data.email)
    if existing_user:
        raise ValueError("Емаил уже зарегистрирован")

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role_id=data.role_id,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


async def login_user(session: AsyncSession, data: LoginRequest) -> dict:

    user = await get_user_by_email(session, data.email)

    if not user:
        raise ValueError("Неверный емаил или пароль")

    if not verify_password(data.password, user.hashed_password):
        raise ValueError("Неверный емаил или пароль")

    role_name = user.role.name

    access_token = create_access_token(user_id=user.id, role=role_name)
    refresh_token = create_refresh_token(user_id=user.id, role=role_name)

    payload_access = decode_token(access_token)
    payload_refresh = decode_token(refresh_token)
    access_jti = payload_access.get("jti")
    refresh_jti = payload_refresh.get("jti")

    await set_value(access_key(access_jti), "1")
    await set_value(refresh_key(refresh_jti), "1")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_access_token(refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except ValueError:
        raise ValueError("Неверный токен")

    if payload.get("type") != "refresh":
        raise ValueError("Неверный тип токена")

    user_id = payload.get("sub")
    role = payload.get("role")

    if not user_id or not role:
        raise ValueError("Неверная загрузка токена")

    new_access_token = create_access_token(user_id=int(user_id), role=role)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
