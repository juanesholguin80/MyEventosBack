from sqlmodel import Session, select
from app.models.user import User


def get_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_by_id(session: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return session.exec(statement).first()


def create(session: Session, user: User) -> User:
    session.add(user)
    session.flush()
    session.refresh(user)
    return user
