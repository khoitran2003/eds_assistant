from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import date, datetime
from pydantic import EmailStr

from app.db.models.general import Gender, Status


# 1. Base Schema: Common fields
class CustomerBase(SQLModel):
    first_name: str = Field(index=True, max_length=255)
    last_name: str = Field(index=True, max_length=255)
    email: EmailStr = Field(unique=True, index=True)
    phone_number: str = Field(index=True, max_length=20)
    gender: Gender
    date_of_birth: date


# 2. Create Schema: For creating a new customer
class CustomerCreate(CustomerBase):
    pass


# 3. Read Schema: For returning customer data to the client
class CustomerRead(CustomerBase):
    id: str
    status: Status
    created_at: datetime
    updated_at: datetime


# 4. Update Schema: For updating an existing customer
class CustomerUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    date_of_birth: Optional[date] = None
