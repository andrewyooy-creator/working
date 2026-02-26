from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password:str

class UserInDB(BaseModel):
    email:EmailStr
    hashed_password: str
