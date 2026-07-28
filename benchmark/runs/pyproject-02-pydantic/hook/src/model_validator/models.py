from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    age: int = Field(ge=0, le=150)
