from pydantic import BaseModel
from datetime import datetime

class PatientHistory(BaseModel):
    event_date: datetime
    event_description: str

class Patient(BaseModel):
    name: str
    age: int
    pesel: str
    medical_history: list[PatientHistory] = []
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str