from app.database import CRUD
from app.tournaments.models import Tourmaments
from app.tournaments import schemas
from sqlalchemy.orm import Session
class Tourmaments_(CRUD):
    @staticmethod
    def create(tourmament_in: schemas.Tourmaments, db: Session) -> Tourmaments:
        new_tourmament = Tourmaments(**tourmament_in.dict())
        CRUD.insert(db, new_tourmament)
        return new_tourmament
