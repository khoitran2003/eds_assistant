"""
FastAPI routes for chat functionality with proper ADK integration.
Demonstrates session management, customer data loading, and agent orchestration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import json
import asyncio
from datetime import datetime

from ...db.base import get_db_session
from ...db.crud.customer import get as get_customer
from ...db.crud.chat_session import (
    create as create_chat_session,
    get as get_chat_session,
    update as update_chat_session,
)
from ...db.schemas.chat import ChatRequest, ChatResponse
from ...db.schemas.chat_session import ChatSessionCreate, ChatSessionUpdate
from ...agent_1 import create_runner, session_service
from ...test_agent import test_agent
from ...utils.log_setup import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


class ChatSessionManager:
    """Manages chat sessions and integrates with ADK session service"""

    @staticmethod
    async def get_or_create_session(
        customer_id: str, session_id: Optional[str], db: Session
    ) -> tuple[str, dict]:
        """
        Get existing session or create new one.
        Returns (session_id, session_metadata)
        """
        try:
            # If session_id provided, try to get existing session
            if session_id:
                chat_session = get_chat_session(db, session_id)
                if chat_session and chat_session.customer_id == int(customer_id):
                    return session_id, {
                        "customer_id": chat_session.customer_id,
                        "created_at": chat_session.created_at.isoformat(),
                        "updated_at": chat_session.updated_at.isoformat(),
                        "status": "existing",
                    }

            # Create new session
            session_create = ChatSessionCreate(
                customer_id=int(customer_id),
                session_data={"created_via": "api", "agent_version": "v2.0"},
            )
            new_session = create_chat_session(db, session_create)

            return str(new_session.id), {
                "customer_id": new_session.customer_id,
                "created_at": new_session.created_at.isoformat(),
                "updated_at": new_session.updated_at.isoformat(),
                "status": "new",
            }

        except Exception as e:
            logger.error(f"Error managing chat session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to manage chat session",
            )

    @staticmethod
    async def initialize_adk_session(
        session_id: str, customer_id: str, runner, db: Session
    ):
        """Initialize ADK session with customer data"""
        try:
            # Get ADK session
            adk_session = runner.get_session(session_id=session_id)

            # Load customer data into session state
            customer = get_customer(db, int(customer_id))
            if customer:
                customer_info = {
                    "id": customer.id,
                    "name": f"{customer.first_name} {customer.last_name}",
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "email": customer.email,
                    "phone": customer.phone_number,
                    "gender": customer.gender.value if customer.gender else None,
                    "status": customer.status.value if customer.status else None,
                }

                # Set customer data in session state
                adk_session.state["customer_id"] = str(customer_id)
                adk_session.state["customer_info"] = customer_info
                adk_session.state["session_initialized"] = True

                logger.info(f"Initialized ADK session for customer: {customer.email}")
            else:
                logger.warning(f"Customer not found: {customer_id}")
                adk_session.state["customer_id"] = str(customer_id)
                adk_session.state["_customer_not_found"] = True

        except Exception as e:
            logger.error(f"Error initializing ADK session: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to initialize session",
            )


@router.post("/start", response_model=ChatResponse)
async def start_chat_session(
    customer_id: str,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db_session),
):
    """
    Start a new chat session or resume existing one.
    Properly initializes ADK session with customer data.
    """
    try:
        # Validate customer exists
        customer = get_customer(db, int(customer_id))
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
            )

        # Get or create chat session
        session_id, session_metadata = await ChatSessionManager.get_or_create_session(
            customer_id, session_id, db
        )

        # Create ADK runner
        runner = create_runner()

        # Initialize ADK session with customer data
        await ChatSessionManager.initialize_adk_session(
            session_id, customer_id, runner, db
        )

        return ChatResponse(
            success=True,
            message="Chat session initialized successfully",
            data={
                "session_id": session_id,
                "customer_name": f"{customer.first_name} {customer.last_name}",
                "session_metadata": session_metadata,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start chat session",
        )


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, db: Session = Depends(get_db_session)):
    """
    Send a message to the chatbot and get response.
    Uses proper ADK session management and agent routing.
    """
    try:
        # Validate session exists
        chat_session = get_chat_session(db, request.session_id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # Create ADK runner
        runner = create_runner()

        # Get ADK session
        adk_session = runner.get_session(session_id=request.session_id)

        # Add user message to session state for callbacks
        adk_session.state["_last_user_message"] = request.message
        adk_session.state["_message_timestamp"] = datetime.utcnow().isoformat()

        # Process message through agent
        response = await runner.run_async(
            session_id=request.session_id,
            message=request.message,
            agent=test_agent,  # You can make this dynamic based on request
        )

        # Update database session
        session_update = ChatSessionUpdate(
            updated_at=datetime.utcnow(),
            session_data={
                "last_message": request.message,
                "last_response": response,
                "message_count": chat_session.session_data.get("message_count", 0) + 1,
            },
        )
        update_chat_session(db, request.session_id, session_update)

        return ChatResponse(
            success=True,
            message="Message processed successfully",
            data={
                "response": response,
                "session_id": request.session_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message",
        )


@router.post("/stream", response_class=StreamingResponse)
async def stream_message(request: ChatRequest, db: Session = Depends(get_db_session)):
    """
    Send a message and get streaming response.
    Demonstrates real-time chat with ADK.
    """
    try:
        # Validate session
        chat_session = get_chat_session(db, request.session_id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        async def generate_response():
            try:
                runner = create_runner()
                adk_session = runner.get_session(session_id=request.session_id)

                # Add user message to state
                adk_session.state["_last_user_message"] = request.message
                adk_session.state["_streaming"] = True

                # Simulate streaming response (ADK may not support true streaming yet)
                response = await runner.run_async(
                    session_id=request.session_id,
                    message=request.message,
                    agent=test_agent,
                )

                # Split response into chunks for streaming effect
                words = response.split()
                for i, word in enumerate(words):
                    chunk = {
                        "chunk": word + " ",
                        "index": i,
                        "done": i == len(words) - 1,
                    }
                    yield f"data: {json.dumps(chunk)}\\n\\n"
                    await asyncio.sleep(0.1)  # Simulate typing delay

            except Exception as e:
                error_chunk = {"error": str(e), "done": True}
                yield f"data: {json.dumps(error_chunk)}\\n\\n"

        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start streaming",
        )


@router.get("/session/{session_id}/state")
async def get_session_state(session_id: str, db: Session = Depends(get_db_session)):
    """
    Get current session state for debugging/monitoring.
    """
    try:
        # Validate session exists in database
        chat_session = get_chat_session(db, session_id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # Get ADK session state
        runner = create_runner()
        adk_session = runner.get_session(session_id=session_id)

        return ChatResponse(
            success=True,
            message="Session state retrieved",
            data={
                "session_id": session_id,
                "adk_state": adk_session.state.to_dict(),
                "db_session": {
                    "id": chat_session.id,
                    "customer_id": chat_session.customer_id,
                    "created_at": chat_session.created_at.isoformat(),
                    "updated_at": chat_session.updated_at.isoformat(),
                    "session_data": chat_session.session_data,
                },
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session state",
        )
