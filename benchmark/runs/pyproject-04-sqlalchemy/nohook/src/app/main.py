from app.db import Base, SessionLocal, engine
from app.models import User


def main() -> None:
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        session.add(User(name="Ada Lovelace", email="ada@example.com"))
        session.commit()

        for user in session.query(User).all():
            print(user.id, user.name, user.email)


if __name__ == "__main__":
    main()
