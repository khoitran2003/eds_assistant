import uuid
from datetime import date, datetime, time
from enum import Enum as EnumType
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, CHAR, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .general import Status

if TYPE_CHECKING:
    from . import Salon


class Location(SQLModel, table=True):
    __tablename__ = "locations"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    location: str = Field(index=True, max_length=255)

    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    salons: List["Salon"] = Relationship(back_populates="location")