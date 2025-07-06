from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel

from app.api.routes import customer, health, root
from app.db.base import engine

# The __init__.py file in app/db/models/ handles the individual imports,
# and this import ensures they are registered with SQLModel's metadata.
import app.db.models


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup events.
    """
    create_db_and_tables()
    yield


app = FastAPI(
    title="Booking Chatbot API",
    description="API for the Booking Chatbot",
    version="1.0.0",
    lifespan=lifespan,
)


# Include the routers from the app/api/routes module
app.include_router(root.router, tags=["Root"])
app.include_router(health.router, tags=["Health"])
app.include_router(customer.router, tags=["Customers"])
