from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.db.models.chat_sessions import ChatSession
from app.db.schemas.chat_session import ChatSessionCreate


def get(*, session: Session, id: UUID) -> Optional[ChatSession]:
    """
    Get a single chat session by ID.
    """
    return session.get(ChatSession, id)


def get_multi_by_customer(
    *, session: Session, customer_id: UUID, skip: int = 0, limit: int = 100
) -> List[ChatSession]:
    """
    Get a list of chat sessions for a specific customer.
    """
    statement = (
        select(ChatSession)
        .where(ChatSession.customer_id == customer_id)
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(statement).all()
    return list(results)


def create(*, session: Session, chat_session_in: ChatSessionCreate) -> ChatSession:
    """
    Create a new chat session.
    """
    db_obj = ChatSession.model_validate(chat_session_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
 