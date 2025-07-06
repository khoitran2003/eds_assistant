from datetime import datetime
from typing import Optional

from sqlalchemy import CHAR, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

class ArtistServiceLink(SQLModel, table=True):
    __tablename__ = "artist_services"  # type: ignore
    artist_id: Optional[str] = Field(
        default=None,
        sa_column=Column(CHAR(36), ForeignKey("artists.id"), primary_key=True),
    )
    service_id: Optional[int] = Field(
        default=None, foreign_key="services.id", primary_key=True
    )
    created_at: datetime = Field(default_factory=datetime.now)