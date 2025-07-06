from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner


from app.api.dependencies import get_db
from app.db import crud
from app.db.schemas.customer import CustomerRead
from app.db.schemas.chat import ChatResponse
from app.test_agent import test_agent

router = APIRouter()

APP_NAME = "Agentic-Chatbot"
SESSION_ID_TOOL_AGENT = "tool_agent"

@router.get("/c", response_model=List[CustomerRead])
def read_customers(
    session: Session = Depends(get_db), skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve customers.
    """
    customers = crud.customer.get_multi(session, skip=skip, limit=limit)
    return customers


@router.get("/c/{customer_id}", response_model=CustomerRead)
def read_customer_by_id(
    customer_id: str,
    session: Session = Depends(get_db),
) -> Any:
    """
    Retrieve a customer by ID.
    """
    customer = crud.customer.get(session=session, id=customer_id)
    return customer

    
    
    



