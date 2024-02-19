from app.database import CRUD
from app.tournaments.models import Tournaments, FootballGames
from app.tournaments import schemas
from sqlalchemy.orm import Session
from typing import List
class Tourmaments_(CRUD):
    @staticmethod
    def create(tourmament_in: schemas.Tourmaments, db: Session) -> Tournaments:
        new_tourmament = Tournaments(**tourmament_in.dict())
        CRUD.insert(db, new_tourmament)
        return new_tourmament
    
    def list_all(db: Session) -> List[Tournaments]:
        return db.query(Tournaments).all()


class FootballGames_(CRUD):
    @staticmethod
    def create(football_game_in: schemas.FootballGames, db: Session) -> FootballGames:
        new_football_game = FootballGames(**football_game_in.dict())
        CRUD.insert(db, new_football_game)
        return new_football_game
    
    def list_all(db: Session) -> List[FootballGames]:
        return db.query(FootballGames).all()