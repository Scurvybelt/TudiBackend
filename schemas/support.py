from pydantic import BaseModel, EmailStr

class HelpRequest(BaseModel):
    fullName: str
    email: EmailStr
    phone: str
    helpType: str
    message: str