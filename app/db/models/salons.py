import uuid
from datetime import date, datetime, time
from enum import Enum as EnumType
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, CHAR, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .general import Status

if TYPE_CHECKING:
    from . import Artist, Location


class Salon(SQLModel, table=True):
    __tablename__ = "salons"  # type: ignore
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(CHAR(36), primary_key=True, index=True),
    )
    location_id: int = Field(foreign_key="locations.id")
    name: str = Field(index=True, max_length=255)
    address: str = Field(index=True, max_length=255)
    phone_number: str = Field(index=True, max_length=20)
    email: str = Field(unique=True, index=True, max_length=255)
    opening_hours: time = Field(index=True)
    closing_hours: time = Field(index=True)
    opening_days: List[str] = Field(
        default=[
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
        ],
        sa_column=Column(JSON),
    )
    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    location: "Location" = Relationship(back_populates="salons")
    artists: List["Artist"] = Relationship(back_populates="salon")