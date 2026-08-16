from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from app.models.entities import UserRole

class LoginRequest(BaseModel): email: EmailStr; password: str = Field(min_length=1)
class UserResponse(BaseModel): id: UUID; email: EmailStr; role: UserRole; full_name: str; permissions: list[str] = []
class TokenResponse(BaseModel): access_token: str; token_type: str = "bearer"; user: UserResponse
