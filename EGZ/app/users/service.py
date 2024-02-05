from app.database import CRUD
from app.users.models import AppUsers
from app.users import schemas
from sqlalchemy.orm import Session
class AppUsers_(CRUD):
    @staticmethod
    def create(user_in: schemas.AppUsers, db: Session) -> AppUsers:
        new_user = AppUsers(**user_in.dict())
        CRUD.insert(db, new_user)
        return new_user
