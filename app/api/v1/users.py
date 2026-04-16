from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.db.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "is_active": current_user.is_active,
    }