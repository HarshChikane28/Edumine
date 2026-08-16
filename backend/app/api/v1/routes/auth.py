from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models import Permission, TeacherPermission, User
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse

router = APIRouter()

async def serialize_user(user: User, db: AsyncSession) -> UserResponse:
    permissions: list[str] = []
    if user.role.value == "teacher":
        result = await db.execute(select(Permission.key).join(TeacherPermission, TeacherPermission.permission_id == Permission.id).where(TeacherPermission.teacher_id == user.id))
        permissions = list(result.scalars().all())
    return UserResponse(id=user.id, email=user.email, role=user.role, full_name=user.full_name, permissions=permissions)

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id, user.role.value), user=await serialize_user(user, db))

@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> UserResponse:
    return await serialize_user(user, db)
