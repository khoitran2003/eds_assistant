from sqlmodel import SQLModel


class ChatMessage(SQLModel):
    message: str


class ChatResponse(SQLModel):
    response: str
