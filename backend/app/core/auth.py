from enum import Enum
from typing import Optional

import httpx
from fastapi import HTTPException, Request, status
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()


class RoleName(Enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    MODERATOR = "MODERATOR"
    TEAM_OWNER = "TEAM_OWNER"
    TEAM_MEMBER = "TEAM_MEMBER"

    @classmethod
    def is_valid_role(cls, role: str) -> bool:
        return role in cls._value2member_map_

    @classmethod
    def is_admin_role(cls, role: str) -> bool:
        return role in {cls.ADMIN.value, cls.SUPER_ADMIN.value, cls.MODERATOR.value}


class User(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    active: bool
    updated_by: Optional[int] = None
    team_name: str
    role_name: str
    accessList: Optional[dict[str, list[str]]] = None


async def get_current_user(request: Request) -> User:
    """Get current authenticated user from token"""
    
    # Development mode bypass
    if settings.DEV_MODE:
        return User(
            user_id=1,
            first_name="Dev",
            last_name="User",
            email=settings.DEV_USER_EMAIL,
            active=True,
            team_name="DEV",
            role_name=settings.DEV_USER_ROLE,
        )
    
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    else:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated"
        )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                settings.ACCESS_VERIFY_TOKEN_URL, 
                params={"tokenId": token},
                timeout=10.0
            )
            
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid token"
                )
            
            # Check if response is JSON
            try:
                user_data = resp.json()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Invalid response from access service: {str(e)}"
                )

            if user_data.get("status") == "failed":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Invalid token"
                )

            return User.model_validate(user_data["data"])
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Access service unavailable: {str(e)}",
            headers={"X-Dependency-Failure": "access_service"},
        )


def require_admin(user: User) -> User:
    """Check if user has admin role"""
    if not RoleName.is_admin_role(user.role_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user
