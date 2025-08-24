from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    # username: str
    name: str
    last_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    # username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    # username: str
    email: EmailStr
    name: str
    last_name: str

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
