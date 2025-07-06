import uuid
from datetime import date, datetime, time
from enum import Enum as EnumType
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, CHAR, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .general import Status
from .linking import ArtistServiceLink

if TYPE_CHECKING:
    from . import Service, Salon, Appointment


class Artist(SQLModel, table=True):
    __tablename__ = "artists"  # type: ignore
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(CHAR(36), primary_key=True, index=True),
    )
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    salon_id: Optional[str] = Field(
        default=None,
        sa_column=Column(CHAR(36), ForeignKey("salons.id"), index=True),
    )
    languages: str = Field(index=True, max_length=255)
    experience_years: int = Field(index=True)
    strengths: Optional[str] = Field(default=None, max_length=1000)
    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    services: List["Service"] = Relationship(
        back_populates="artists", link_model=ArtistServiceLink
    )
    salon: "Salon" = Relationship(back_populates="artists")
    appointments: List["Appointment"] = Relationship(back_populates="artist")
