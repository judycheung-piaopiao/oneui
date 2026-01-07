"""
Admin management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.auth import get_current_user, User
from app.db.base import get_db

router = APIRouter()


@router.get("/is-admin")
async def check_admin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if current user is an admin"""
    try:
        result = await db.execute(
            text("SELECT COUNT(*) FROM admins WHERE email = :email"),
            {"email": user.email}
        )
        count = result.scalar()
        return {"is_admin": count > 0, "email": user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_admins(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all admins (requires admin access)"""
    # Check if requester is admin
    try:
        result = await db.execute(
            text("SELECT COUNT(*) FROM admins WHERE email = :email"),
            {"email": user.email}
        )
        is_admin = result.scalar()
        if not is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        result = await db.execute(
            text("SELECT email, added_at, added_by FROM admins ORDER BY added_at")
        )
        admins = result.fetchall()
        return {
            "admins": [
                {
                    "email": row[0],
                    "added_at": row[1].isoformat() if row[1] else None,
                    "added_by": row[2]
                }
                for row in admins
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/add")
async def add_admin(
    email: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new admin (requires admin access)"""
    try:
        # Check if requester is admin
        result = await db.execute(
            text("SELECT COUNT(*) FROM admins WHERE email = :email"),
            {"email": user.email}
        )
        is_admin = result.scalar()
        if not is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        await db.execute(
            text("INSERT INTO admins (email, added_by) VALUES (:email, :added_by)"),
            {"email": email, "added_by": user.email}
        )
        await db.commit()
        return {"success": True, "email": email}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/remove")
async def remove_admin(
    email: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove an admin (requires admin access)"""
    try:
        # Check if requester is admin
        result = await db.execute(
            text("SELECT COUNT(*) FROM admins WHERE email = :email"),
            {"email": user.email}
        )
        is_admin = result.scalar()
        if not is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Prevent removing yourself
        if email == user.email:
            raise HTTPException(status_code=400, detail="Cannot remove yourself")
        
        await db.execute(
            text("DELETE FROM admins WHERE email = :email"),
            {"email": email}
        )
        await db.commit()
        return {"success": True, "email": email}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
