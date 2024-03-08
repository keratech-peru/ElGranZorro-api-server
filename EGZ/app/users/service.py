from app.database import CRUD
from app.users.models import AppUsers
from app.users import schemas
from sqlalchemy.orm import Session
from typing import List
class AppUsers_(CRUD):
    @staticmethod
    def create(user_in: schemas.AppUsers, db: Session) -> AppUsers:
        new_user = AppUsers(**user_in.dict())
        CRUD.insert(db, new_user)
        return new_user
    
    def list_all(db: Session) -> List[AppUsers]:
        return db.query(AppUsers).all()
