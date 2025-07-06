from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_root():
    """
    Root endpoint.
    """
    return {"message": "Hello, World! This is the Booking Chatbot API"}
