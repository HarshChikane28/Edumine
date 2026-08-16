from collections.abc import Callable
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Permission, TeacherPermission, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try: payload = decode_access_token(token); user_id = UUID(payload["sub"])
    except (ValueError, KeyError, TypeError): raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = await db.get(User, user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Inactive or missing user")
    return user

def require_role(*roles: str) -> Callable:
    async def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role.value not in roles: raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency

def require_permission(key: str) -> Callable:
    async def dependency(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> User:
        if user.role.value == "admin": return user
        if user.role.value != "teacher": raise HTTPException(status_code=403, detail="Insufficient role")
        query = select(TeacherPermission.id).join(Permission, Permission.id == TeacherPermission.permission_id).where(TeacherPermission.teacher_id == user.id, Permission.key == key)
        if not (await db.scalar(query)): raise HTTPException(status_code=403, detail=f"Missing permission: {key}")
        return user
    return dependency
