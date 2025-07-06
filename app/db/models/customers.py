import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import CHAR, Column
from sqlmodel import Field, Relationship, SQLModel

from .general import Status, Gender

if TYPE_CHECKING:
    from . import Appointment, ChatSession


class Customer(SQLModel, table=True):
    __tablename__ = "customers"  # type: ignore
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(CHAR(36), primary_key=True, index=True),
    )
    first_name: str = Field(index=True, max_length=255)
    last_name: str = Field(index=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    phone_number: str = Field(index=True, max_length=20)
    gender: Gender = Field(index=True)
    date_of_birth: date = Field(index=True)

    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    appointments: List["Appointment"] = Relationship(back_populates="customer")
    chat_sessions: List["ChatSession"] = Relationship(back_populates="customer")
