from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session


class Base(DeclarativeBase):
    pass


engine = create_engine("sqlite:///app.db")


def get_session() -> Session:
    return Session(engine)
