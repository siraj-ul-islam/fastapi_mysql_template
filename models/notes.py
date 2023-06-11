import datetime
from typing import Optional, List
from pydantic import BaseModel

class NoteBase(BaseModel):
    title: str
    content: Optional[str] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteDB(NoteBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: int


class User(UserBase):
    name: str


class UserDB(UserBase):
    pass