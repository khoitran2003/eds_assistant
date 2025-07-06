import uuid
from datetime import datetime
from sqlmodel import SQLModel


# Base schema with common fields
class ChatSessionBase(SQLModel):
    customer_id: uuid.UUID


# Schema for creating a chat session
class ChatSessionCreate(ChatSessionBase):
    pass


# Schema for reading a chat session (e.g., in an API response)
class ChatSessionRead(ChatSessionBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Schema for updating a chat session (if needed)
class ChatSessionUpdate(SQLModel):
    # For now, it's empty as updates might be handled automatically (e.g., updated_at).
    pass
