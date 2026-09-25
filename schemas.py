from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: bool = False


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    completed: bool
    owner_id: int
