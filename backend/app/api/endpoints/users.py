from fastapi import APIRouter, Depends

from app.core.auth import User, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def read_current_user(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return current_user
