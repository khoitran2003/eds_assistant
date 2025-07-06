from __future__ import annotations
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CHAR, Column, DateTime, ForeignKey
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from . import Customer


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"  # type: ignore

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(CHAR(36), primary_key=True, nullable=False, index=True),
    )
    customer_id: str = Field(
        sa_column=Column(CHAR(36), ForeignKey("customers.id"), nullable=False)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, nullable=False, default=datetime.utcnow),
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=datetime.now,
            onupdate=datetime.now,
        ),
    )

    # Relationship to Customer - use string forward reference for consistency
    customer: Customer = Relationship(back_populates="chat_sessions")
