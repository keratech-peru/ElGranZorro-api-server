from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import SQLALCHEMY_DATABASE_URI
from typing import Generator, List, Generic, TypeVar


engine = create_engine(SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


T = TypeVar("T")


class CRUD(Generic[T]):
    @staticmethod
    def retrieve_all(db: Session, model: T) -> List[T]:
        return db.query(model).all()

    @staticmethod
    def insert(db: Session, model: T) -> None:
        db.add(model)
        db.commit()
        db.refresh(model)

    @staticmethod
    def update(db: Session, model: T) -> None:
        db.commit()
        db.refresh(model)

    @staticmethod
    def delete(db: Session, model: T) -> None:
        db.query(model).delete()

    @staticmethod
    def bulk_insert(db: Session, model_list: list[T]) -> None:
        db.add_all(model_list)
        db.commit()