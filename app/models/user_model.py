from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    name: str
    email: EmailStr
    picture: str
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
