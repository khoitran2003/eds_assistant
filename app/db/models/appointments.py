import uuid
from datetime import date, datetime, time
from enum import Enum as EnumType
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, CHAR, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .general import Status

if TYPE_CHECKING:
    from . import Customer, Service, Artist


class Appointment(SQLModel, table=True):
    __tablename__ = "appointments"  # type: ignore

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(CHAR(36), primary_key=True, index=True),
    )
    customer_id: Optional[str] = Field(
        default=None,
        sa_column=Column(CHAR(36), ForeignKey("customers.id"), index=True),
    )
    artist_id: Optional[str] = Field(
        default=None,
        sa_column=Column(CHAR(36), ForeignKey("artists.id"), index=True),
    )
    service_id: Optional[int] = Field(
        default=None, foreign_key="services.id", index=True
    )
    appointment_time: datetime = Field(index=True)
    note: Optional[str] = Field(default=None, max_length=1000)

    status: Status = Field(default=Status.PENDING, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    customer: "Customer" = Relationship(back_populates="appointments")
    artist: "Artist" = Relationship(back_populates="appointments")
    service: "Service" = Relationship(back_populates="appointments")
