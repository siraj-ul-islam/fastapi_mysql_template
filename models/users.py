import datetime
from typing import Optional
from pydantic import BaseModel



# Define the input schema for creating a user
class UsersInSchema(BaseModel):
    name: str
    password: str
    email: str
    # email_verified_at: datetime.datetime
    profile_image: str = None
    # remember_token: str
    user_type: str
    credit: str = None
    created_at: datetime.datetime
    # updated_at: datetime.datetime


# Define the output schema for retrieving a user
class UsersSchema(BaseModel):
    id: int
    name: str
    # password: str
    remember_token: str = None
    user_type: str
    credit: str = None
    email: str


# Define the schema for logging in
class LogInSchema(BaseModel):
    name: str
    password: str


class TokenData(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None
    user_type: Optional[str] = None