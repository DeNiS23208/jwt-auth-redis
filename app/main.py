from fastapi import FastAPI
from sqlalchemy import select

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.content import router as content_router
from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.db.models.role import Role
from app.db.models.user import User
from app.db.models.content import Content



app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(content_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Role).where(Role.name == "role1"))
        role1 = result.scalar_one_or_none()

        if not role1:
            session.add(Role(name="role1"))

        result = await session.execute(select(Role).where(Role.name == "role2"))
        role2 = result.scalar_one_or_none()

        if not role2:
            session.add(Role(name="role2"))

        await session.commit()


@app.get("/")
async def root():
    return {"message": "API is working"}