import uuid
from datetime import date, datetime, time
from enum import Enum as EnumType
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import JSON, CHAR, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

from .general import Status
from .linking import ArtistServiceLink

if TYPE_CHECKING:
    from . import Appointment, Artist, ServiceCategory, ServiceSubCategory


class ServiceDetail(SQLModel, table=True):
    __tablename__ = "service_details"  # type: ignore
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(CHAR(36), primary_key=True, index=True),
    )
    service_id: Optional[int] = Field(
        default=None, foreign_key="services.id", index=True
    )

    description: Optional[str] = Field(default=None, max_length=1000)
    duration: Optional[int] = Field(default=None, index=True)
    listed_price: Optional[float] = Field(default=None, index=True)
    listed_price_2_sessions: Optional[float] = Field(default=None, index=True)
    currency: str = Field(default="AUD", index=True, max_length=10)

    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    service: "Service" = Relationship(back_populates="service_details")


class Service(SQLModel, table=True):
    __tablename__ = "services"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    sub_category_id: Optional[int] = Field(
        default=None, foreign_key="service_sub_categories.id", index=True
    )
    category_id: Optional[int] = Field(
        default=None, foreign_key="service_categories.id", index=True
    )
    name: str = Field(index=True, max_length=255)

    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    service_details: List["ServiceDetail"] = Relationship(back_populates="service")
    appointments: List["Appointment"] = Relationship(back_populates="service")
    artists: List["Artist"] = Relationship(
        back_populates="services", link_model=ArtistServiceLink
    )
    service_sub_category: "ServiceSubCategory" = Relationship(back_populates="services")
    service_category: "ServiceCategory" = Relationship(back_populates="services")


class ServiceCategory(SQLModel, table=True):
    __tablename__ = "service_categories"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, max_length=255)

    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    services: List[Service] = Relationship(back_populates="service_category")
    service_sub_categories: List["ServiceSubCategory"] = Relationship(
        back_populates="service_category"
    )


class ServiceSubCategory(SQLModel, table=True):
    __tablename__ = "service_sub_categories"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, max_length=255)
    category_id: Optional[int] = Field(
        default=None, foreign_key="service_categories.id", index=True
    )

    status: Status = Field(default=Status.ACTIVE, index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )

    # Relationships
    service_category: "ServiceCategory" = Relationship(
        back_populates="service_sub_categories"
    )
    services: List[Service] = Relationship(back_populates="service_sub_category")
