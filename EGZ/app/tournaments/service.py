from app.database import CRUD
from app.tournaments.models import Tourmaments
from app.tournaments import schemas
from sqlalchemy.orm import Session
from typing import List
class Tourmaments_(CRUD):
    @staticmethod
    def create(tourmament_in: schemas.Tourmaments, db: Session) -> Tourmaments:
        new_tourmament = Tourmaments(**tourmament_in.dict())
        CRUD.insert(db, new_tourmament)
        return new_tourmament
    
    def list_all(db: Session) -> List[Tourmaments]:
        return db.query(Tourmaments).all()
