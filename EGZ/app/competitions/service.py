import random
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.exception import validate_credentials, expired_token
from app.database import CRUD
from app.competitions.models import Matchs
from app.competitions import schemas
from app.tournaments.models import FootballGames



class Competitions_(CRUD):
    @staticmethod
    def create(db: Session):
        compe_1 = Competitions(
            id_competition=2013,
            name="Campeonato Brasileiro Série A",
            code="BSA",
            type="LEAGUE",
            emblem="https://crests.football-data.org/bsa.png"
        )
        compe_2 = Competitions(
            id_competition=2002,
            name="Bundesliga",
            code="BL1",
            type="LEAGUE",
            emblem="https://crests.football-data.org/BL1.png"
        )
        compe_3 = Competitions(
            id_competition=2003,
            name="Eredivisie",
            code="DED",
            type="LEAGUE",
            emblem="https://crests.football-data.org/ED.png"
        )

        compe_4 = Competitions(
            id_competition=2014,
            name="Primera Division",
            code="PD",
            type="LEAGUE",
            emblem="https://crests.football-data.org/PD.png"
        )
        compe_5 = Competitions(
            id_competition=2015,
            name="Ligue 1",
            code="FL1",
            type="LEAGUE",
            emblem="https://crests.football-data.org/FL1.png"
        )
        objects_list = [compe_1, compe_2, compe_3, compe_4, compe_5]
        CRUD.bulk_insert(db, objects_list)
    
    @staticmethod
    def assignment(db: Session, tournament_id: int):
        footballgames = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id).all()
        days = set([footballgame.date for footballgame in footballgames])
        for day in days:
            footballgames_by_day = db.query(FootballGames).filter(FootballGames.tournament_id == tournament_id, FootballGames.date == day).all()
            matchs = random.sample( db.query(Matchs).filter(Matchs.date == day).all(), len(footballgames_by_day))
            for i in range(len(footballgames_by_day)):
                print(matchs[i])
                #footballgames_by_day[i]

