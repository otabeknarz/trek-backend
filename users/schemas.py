from datetime import datetime
from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    phone_number: str
    password: str


class UserCheckPasswordSchema(BaseModel):
    username: str
    password: str


class UserResponseSchema(BaseModel):
    id: int
    username: str
    phone_number: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
