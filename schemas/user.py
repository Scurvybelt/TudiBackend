from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    name: str
    last_name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    last_name: str

    class Config:
        from_attributes = True
