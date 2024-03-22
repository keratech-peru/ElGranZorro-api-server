from app.database import CRUD
from app.users.models import PlaysUsers
from app.tournaments.models import Tournaments, FootballGames, GroupStage
from app.tournaments import schemas
from app.tournaments.constants import GROUPS
from sqlalchemy.orm import Session
from typing import List 
from datetime import datetime, timezone, timedelta
import pytz
from fastapi.encoders import jsonable_encoder
class Tournaments_(CRUD):
    @staticmethod
    def create(tourmament_in: schemas.Tourmaments, db: Session) -> Tournaments:
        new_tourmament = Tournaments(**tourmament_in.dict())
        CRUD.insert(db, new_tourmament)
        return new_tourmament
    
    def list_all(db: Session) -> List[Tournaments]:
        return db.query(Tournaments).all()
    
    def get_footballgames(db: Session, tournament_id: int, user_id: int):
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id).all()
        datetime_now = datetime.now(pytz.timezone("America/Lima"))
        football_of_the_day = []
        football_past = []
        for footballgame in footballgames:
            dif = datetime_now - datetime.strptime(footballgame.date, '%d/%m/%y').replace(tzinfo=timezone.utc)
            footballgame_dict = footballgame.__dict__
            play_user = db.query(PlaysUsers).filter(PlaysUsers.id == footballgame.id,PlaysUsers.appuser_id == user_id).first()
            if int(dif.days) == 0:
                del footballgame_dict["home_score"]
                del footballgame_dict["away_score"]
                footballgame_dict["score_local_user"] = play_user["score_local"] if play_user else None
                footballgame_dict["score_visit_user"] = play_user["score_local"] if play_user else None
                football_of_the_day.append(footballgame_dict)
            if int(dif.days) > 0:
                footballgame_dict["score_local_user"] = play_user["score_local"] if play_user else None
                footballgame_dict["score_visit_user"] = play_user["score_local"] if play_user else None
                football_past.append(footballgame_dict)
        return football_of_the_day, football_past


class FootballGames_(CRUD):
    @staticmethod
    def create(football_game_in: schemas.FootballGames, db: Session) -> FootballGames:
        new_football_game = FootballGames(**football_game_in.dict())
        CRUD.insert(db, new_football_game)
        return new_football_game

    def update(footballgame_id:int , update_footballgame_in: schemas.UpdateFootballGames, db: Session) :
        footballgame = db.query(FootballGames).filter(FootballGames.id == footballgame_id).first()
        if footballgame:
            footballgame.home_team = update_footballgame_in.home_team
            footballgame.away_team = update_footballgame_in.away_team
            footballgame.home_score = update_footballgame_in.home_score
            footballgame.away_score = update_footballgame_in.away_score
            CRUD.update(db, footballgame)       

    def list_all(db: Session) -> List[FootballGames]:
        # db.query(FootballGames, Tournaments.codigo).join(Tournaments).all()
        data = jsonable_encoder(db.query(FootballGames).all())
        for i in range(len(data)):
            data[i]["tournament_codigo"] = db.query(Tournaments.codigo).filter(Tournaments.id == data[i]["tournament_id"]).first()[0]
        return data
    
    def create_groups_stage(id: int , codigo:str, start_date:str, db: Session):
        cont = 0
        for i in range(1,4):
            for j in range(1,4):
                cont = cont + 1
                date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = i-1)
                obj_temp = schemas.FootballGames(
                    codigo=codigo+'GP'+str(cont),
                    tournament_id=id,
                    tournament_stage=f"Fecha {i} - GRUPOS",
                    date=datetime.strftime(date,'%d/%m/%y'),
                    type_footballgames= "RESULT" if i*j%2 == 0 else "SCORE",
                    home_team=None,
                    away_team=None,
                    home_score=None,
                    away_score=None                                                                                     
                )
                CRUD.insert(db, FootballGames(**obj_temp.dict()))
        
        for group in GROUPS:
            for i in range(4):
                obj_temp = schemas.GroupStage(tournament_cod=codigo, group=group)
                CRUD.insert(db, GroupStage(**obj_temp.dict()))
    
    def create_eighths_stage(id: int , codigo:str, start_date:str, db: Session):
        cont = 0
        for i in range(1,4):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 3)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'OC'+str(cont),
                tournament_id=id,
                tournament_stage=f"OCTAVOS",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            CRUD.insert(db, FootballGames(**obj_temp.dict()))

    def create_quarter_stage(id: int , codigo:str, start_date:str, db: Session):
        cont = 0
        for i in range(1,4):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 4)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'CU'+str(cont),
                tournament_id=id,
                tournament_stage=f"CUARTOS",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            CRUD.insert(db, FootballGames(**obj_temp.dict()))

    def create_semifinal_stage(id: int , codigo:str, start_date:str, db: Session):
        cont = 0
        for i in range(1,4):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 5)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'SF'+str(cont),
                tournament_id=id,
                tournament_stage=f"SEMI-FINAL",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            CRUD.insert(db, FootballGames(**obj_temp.dict()))

    def create_final_stage(id: int , codigo:str, start_date:str, db: Session):
        cont = 0
        for i in range(1,6):
            cont = cont + 1
            date = datetime.strptime(start_date, '%d/%m/%y') + timedelta(days = 6)
            obj_temp = schemas.FootballGames(
                codigo=codigo+'FI'+str(cont),
                tournament_id=id,
                tournament_stage=f"FINAL",
                date=datetime.strftime(date,'%d/%m/%y'),
                type_footballgames= "RESULT" if i%2 == 0 else "SCORE",
                home_team=None,
                away_team=None,
                home_score=None,
                away_score=None                                                                                     
            )
            CRUD.insert(db, FootballGames(**obj_temp.dict()))

