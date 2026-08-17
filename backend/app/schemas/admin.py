from uuid import UUID
from pydantic import BaseModel, Field
class TeacherCreate(BaseModel): email: str = Field(min_length=3); password: str = Field(min_length=8); full_name: str; permissions: list[str] = []
class TeacherPermissionUpdate(BaseModel): permissions: list[str]
class StudentCreate(BaseModel): email: str = Field(min_length=3); password: str = Field(min_length=8); full_name: str; class_id: UUID; roll_no: str; student_code: str
