from sqlmodel import create_engine, Session
from ..utils import get_all_env_vars

ENV_VARS = get_all_env_vars()

HOST = ENV_VARS["DB_HOST"]
USER = ENV_VARS["DB_USER"]
PASSWORD = ENV_VARS["DB_PASSWORD"]
PORT = ENV_VARS["DB_PORT"]
DB_NAME = ENV_VARS["BOOKING_CHATBOT_DB"]

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def get_db_session():
    with Session(engine) as session:
        yield session
