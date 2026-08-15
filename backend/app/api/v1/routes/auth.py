from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()
class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(payload: LoginRequest) -> dict:
    return {"access_token": "local-demo-token", "token_type": "bearer", "user": {"id": "student-1", "role": "student", "name": "Shashi Kant"}}

@router.get("/me")
async def me() -> dict:
    return {"id": "student-1", "role": "student", "name": "Shashi Kant"}
