from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.db.models.content import Content


router = APIRouter(prefix="/content", tags=["Content"])


@router.get("/")
async def get_content(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):

    user_role = current_user.role.name

    # Здесь можно реализовать логику доступа к контенту в зависимости от роли пользователя
    # логика доступа
    if user_role == "role1":
        query = select(Content).where(Content.access_level.in_(["common", "role1"]))
    elif user_role == "role2":
        query = select(Content).where(Content.access_level.in_(["common", "role2"]))
    else:
        query = select(Content).where(Content.access_level == "common")

    result = await db.execute(query)
    contents = result.scalars().all()

    return contents
