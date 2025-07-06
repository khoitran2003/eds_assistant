from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Annotated
from datetime import date, datetime
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"


class CustomerProfileBase(BaseModel):
    user_id: Annotated[str, Field(min_length=36, max_length=36)]
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None


class CustomerProfileCreate(CustomerProfileBase):
    pass


class CustomerProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[GenderEnum] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None


class CustomerProfileOut(CustomerProfileBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
