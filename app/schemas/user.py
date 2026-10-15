from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.enums import RoleEnum


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    full_name: str
    role: RoleEnum
    is_active: bool
